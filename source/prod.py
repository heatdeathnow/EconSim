from __future__ import annotations
from functools import cached_property, lru_cache
from math import isclose
from typing import Optional

from source.exceptions import NegativeAmountError
from source.goods import Goods, Stockpile
from source.pop import ComFactory, Community, Jobs, Pop, PopFactory, Strata

class Extractor:

    THROUGHPUT = 1.25  # This is a placeholder value while the feature does not yet exist. This will be embedded to the `Good` class.

    def __init__(self, product: Goods, workforce: Community, needed_workers: dict[Jobs, int | float]) -> None:
        self.product = product
        self.workforce = workforce
        self.needed_workers = needed_workers

    def __repr__(self) -> str:
        pops = self.workforce.values()
        pops = list(map(str, pops))
        return f"<{self.product} Extractor obj.: {', '.join(pops)} >"

    @staticmethod
    def __fix_dict[T](to_fix: dict[T, int | float]) -> None:

        for key, val in to_fix.copy().items():
            if isclose(val, 0):
                del to_fix[key]

    @cached_property
    def __employable_strata(self) -> set[Strata]:
        return {job.stratum for job in self.needed_workers}

    @cached_property
    def capacity(self) -> float:
        return sum(self.needed_workers.values())

    def calc_total_workers(self) -> float:
        return sum(pop.size for pop in self.workforce.values())
    
    def calc_efficiency(self) -> float:
        """
        Efficiency is the measurement of how well the workforce actually fits to the needed jobs. This values should always
        range between 0.0 and 1.0. The former representing inability to produce and the latter representing working in perfect conditions.
        
        Let's say an `Extractor` object needs 100 farmers. If it has 100 farmers, then it will have 1.0 efficiency. 
        If it has 50 farmers then it will have 0.5 efficiency. If it has 0 farmers, then it will have 0.0 efficiency.

        Let's say an `Extractor` object needs 100 farmers and 100 miners - it would therefore have a capacity for 200 workers.
        If it has 150 farmers and 50 miners, the efficiency calculation would go as follows. 1.0 for the farmers plus 0.5 for the miners
        divided by the amount of different jobs, this case 2, therefore 0.75 efficiency.
        """

        efficiency = 0.0

        for job, needed in self.needed_workers.items():

            # Due to the nature of the `Community` class, this will never cause a KeyError.
            efficiency += min(1, self.workforce[job].size / needed)
        
        # ZeroDivisionError should never occour since creating `Extractor` objects 
        # with an empty `needed_workers` attribute itself raises an error.
        efficiency /= len(self.needed_workers)

        return efficiency

    def produce(self) -> Stockpile:
        return Stockpile({self.product: Extractor.THROUGHPUT * self.calc_total_workers() * self.calc_efficiency()})

    @lru_cache
    def calc_labor_demand(self) -> dict[Jobs, int | float]:
        """ Returns a `dict[Jobs, int | float]` representing how many workers from a specific job are needed to fill up to capacity. """

        available_space = self.capacity - self.calc_total_workers()

        if available_space <= 0: return {}

        labor_demand = {job: 0.0 for job in self.needed_workers}

        for job, needed in self.needed_workers.items():
            missing = max(0, needed - self.workforce[job].size)
            labor_demand[job] = missing
        
        self.__fix_dict(labor_demand)
        total_needed = sum(labor_demand.values())

        if total_needed < available_space:
            return labor_demand
        
        weights = {job: needed / total_needed for job, needed in labor_demand.items()}
        labor_demand = {job: weight * available_space for job, weight in weights.items()}

        self.__fix_dict(labor_demand)
        return labor_demand

    def calc_goods_demand(self) -> Stockpile:
        """ Calculate a `Stockpile` object representing how many goods the pops inside this `Extractor` object need. """
    
        goods_demand = Stockpile()

        for pop in self.workforce.values():
            goods_demand += pop.calc_consumption()

        return goods_demand
    
    def can_employ(self, __value: Pop) -> bool:
        """ This method does not care about amounts, for excess amounts will just be left in the original `Pop` object. """

        if __value.job in self.calc_labor_demand():
            return True
        
        if __value.job == Jobs.NONE and __value.stratum in self.__employable_strata:
            return True
        
        return False

    def employ(self, pop: Pop) -> None:
        """ Employs a pop assuming its job is either demanded or `Jobs.NONE`. """

        labor_demand = self.calc_labor_demand()

        if pop.job == Jobs.NONE:
            for job in pop.stratum.jobs:
                if job in labor_demand:  # TODO: a better way of choosing a job in this case. Something with priorities.
                    employed = PopFactory.job(job, min(pop.size, labor_demand[job]), pop.welfare)
                    self.workforce += employed
                    pop -= employed

        else:
            # If this method is used as intended (after checking the `can_employ` method), 
            # there will never be a  KeyError in accessing `labor_demand`.
            employed = PopFactory.job(pop.job, min(pop.size, labor_demand[pop.job]), pop.welfare)
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
            return Extractor(product, workforce, needed_workers)
        
        elif isinstance(workforce, dict):
            return Extractor(product, ComFactory.job(workforce), needed_workers)
        
        else:
            return Extractor(product, ComFactory.job(), needed_workers)
    
    @classmethod
    def full(cls,
             product: Goods,
             needed_workers: dict[Jobs, int | float]):
        
        cls.__validate_product(product)
        cls.__validate_needed_workers(needed_workers)

        return Extractor(product, ComFactory.job(needed_workers), needed_workers)
    