from __future__ import annotations
from functools import cached_property, lru_cache
from math import isclose
from typing import Optional

from source.exceptions import NegativeAmountError
from source.goods import Goods, Stockpile
from source.pop import ComFactory, Community, Jobs, Pop, PopFactory, Strata

class Extractor:

    THROUGHPUT = 1.25  # This is a placeholder value while the feature does not yet exist. This will be embedded to the `Good` class.

    def __init__(self, product: Goods, needed_workers: dict[Jobs, int | float], workforce: Community) -> None:
        self.product = product
        self.workforce = workforce
        self.needed_workers = needed_workers

    def __repr__(self) -> str:
        pops = self.workforce.values()
        pops = list(map(str, pops))
        return f"<{self.product.name} Extractor obj.: {', '.join(pops)} >"

    @cached_property
    def capacity(self) -> float:
        return sum(self.needed_workers.values())

    @cached_property
    def efficient_shares(self) -> dict[Jobs, float]:
        return {job: amount / self.capacity for job, amount in self.needed_workers.items()}

    def calc_efficiency(self) -> float:
        """
        This method calculates the efficiency of production based on how well the proportion of the workers in the `Extractor` 
        object conform to the efficienct_share.

        Because of the nature of the algorithm used to calculate this, efficiency will always reach 0 when there are 0 workers
        or when there are double the workers needed for that particular job.
        """

        total_difference = 0.0

        for job, efficient_share in self.efficient_shares.items():

            share = self.workforce.get_share_of(job)

            difference = abs(efficient_share - share)
            weighted_difference = min(1, difference / efficient_share)

            total_difference += weighted_difference            

        mean_difference = total_difference / len(self.efficient_shares)
        efficiency = 1.0 - mean_difference

        return efficiency

    def produce(self) -> Stockpile:
        return Stockpile({self.product: Extractor.THROUGHPUT * self.workforce.size * self.calc_efficiency()})

    @lru_cache
    def calc_labor_demand(self) -> Community:
        """ Returns a `dict[Jobs, int | float]` representing how many workers from a specific job are needed to fill up to capacity. """

        available_space = self.capacity - self.workforce.size

        if available_space <= 0: return Community()

        labor_demand = Community()

        for job, needed_pop in self.needed_workers.items():
            missing = max(0, needed_pop - self.workforce[job].size)
            labor_demand += PopFactory.job(job, missing)
        
        total_needed = labor_demand.size

        if total_needed < available_space:
            return labor_demand

        weights = {job: pop.size / total_needed for job, pop in labor_demand.items()}  # job will never be `tuple[Strata, Jobs.NONE]``
        labor_demand = ComFactory.job({job: weight * available_space for job, weight in weights.items()})  # type: ignore

        return labor_demand
    
    def can_employ(self, __value: Pop) -> bool:
        """ This method does not care about amounts, for excess amounts will just be left in the original `Pop` object. """

        labor_demand = self.calc_labor_demand()

        if __value.job in labor_demand:
            return True
        
        if __value.job == Jobs.NONE and len(labor_demand[__value.stratum]) > 0:
            return True
        
        return False

    def employ(self, pop: Pop) -> None:
        """ 
        Employs a pop assuming its job is either demanded or `Jobs.NONE`. If the job is `Jobs.NONE`, it is assumed 
        that the pop's stratum has jobs that are demanded by this `Extractor`.

        This modifies the passed `pop` argument in place. It removes the workers from it that were employed by this `Extractor`.
        """

        labor_demand = self.calc_labor_demand()

        if pop.job == Jobs.NONE:
            job = max(labor_demand[pop.stratum].values()).job
            
        else:
            job = pop.job

        employed = PopFactory.job(job, min(pop, labor_demand[job]).size, pop.welfare)
        self.workforce += employed
        pop -= employed

class ExtFactory:

    @staticmethod
    def __validate_product(product: Goods) -> None:
        if product not in Goods:
            raise TypeError(f'`product` argument must be a member of `Goods`, not "{product}".')
    
    @staticmethod
    def __validate_needed_workers(needed_workers: dict[Jobs, int | float]) -> None:
        if not isinstance(needed_workers, dict):
            raise TypeError(f'`needed_workers` argument must be an instance of a dictionary, not {type(needed_workers)}.')
        
        if len(needed_workers) < 1:
            raise ValueError(f'`needed_workers` argument cannot be an empty dictionary.')

        for job, amount in needed_workers.items():
            if job not in Jobs:
                raise TypeError(f'All keys of `needed_workers` argument must be members of `Jobs` not {job}.')
            
            if job == Jobs.NONE:
                raise ValueError(f'`Jobs.NONE` is not valid for Extractor creation.')
            
            if not isinstance(amount, (int, float)):
                raise TypeError(f'All values of `needed_workers` argument must be integers or floats, but got {amount}.')
            
            if amount < 0:
                raise NegativeAmountError(f'All values of `needed_workers` argument must be positive, but got {amount}.')
    
    @staticmethod
    def __validate_workforce(needed_workers: dict[Jobs, int | float], workforce: Community | dict[Jobs, int | float] | None):
        if workforce is None: return

        capacity = sum(needed_workers.values())
        total = 0

        if isinstance(workforce, Community):
            for job, pop in workforce.items():
                if job not in needed_workers:
                    raise ValueError(f'The the job of {pop} does not conform to the passed `needed_workers` argument.')
                
                total += pop.size

        elif isinstance(workforce, dict):
            for job, pop in workforce.items():
                if job not in Jobs:
                    raise TypeError(f'The key "{job}" in the workforce dictionary is not a member of `Jobs`.')

                if not isinstance(pop, (int, float)):
                    raise TypeError(f'The value "{pop}" in the workforce dictionary is not an `int` or a `float`.')

                if job not in needed_workers:
                    raise ValueError(f'The the job of {pop} does not conform to the passed `needed_workers` argument.')
                
                total += pop

        else:
            raise TypeError(f'`workforce` argument must be either a `Community` object or a dict.')

        if total > capacity:
            raise ValueError(f'Total size of the passed workforce {workforce} is greater than the would-be capacity of the Extractor.')

    @classmethod
    def default(cls,
                product: Goods,
                needed_workers: dict[Jobs, int | float],
                workforce: Optional[Community | dict[Jobs, int | float]] = None) -> Extractor:

        cls.__validate_product(product)
        cls.__validate_needed_workers(needed_workers)
        cls.__validate_workforce(needed_workers, workforce)

        if isinstance(workforce, Community):
            return Extractor(product, needed_workers, workforce)
        
        elif isinstance(workforce, dict):
            return Extractor(product, needed_workers, ComFactory.job(workforce))
        
        else:
            return Extractor(product, needed_workers, ComFactory.job())
    
    @classmethod
    def full(cls,
             product: Goods,
             needed_workers: dict[Jobs, int | float]):
        
        cls.__validate_product(product)
        cls.__validate_needed_workers(needed_workers)

        return Extractor(product, needed_workers, ComFactory.job(needed_workers))
    