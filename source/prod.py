from __future__ import annotations
from abc import ABC, abstractmethod
import copy
from decimal import Decimal, getcontext
from inspect import isclass
from math import isclose
from typing import TYPE_CHECKING, Optional, overload
from source.exceptions import CannotEmployError, NegativeAmountError
from source.goods import Techs, Technology, Products, Stock, create_good, create_stock
from source.pop import CommuneFactory, Commune, Jobs, Pop, PopFactory
D = getcontext().create_decimal

if TYPE_CHECKING:
    from source.algs import balance_alg
    from source import goods_dict, pop_dict


class Industry(ABC):

    def __init__(self, product: Products,
                 prod_tech: Techs,
                 production: Technology,
                 needed_workers: dict[Jobs, Decimal],
                 workforce: Commune, /) -> None:
        
        self.product = product
        self.prod_tech = prod_tech
        self.production = production
        self.workforce = workforce
        self.needed_workers = needed_workers

    def __repr__(self) -> str:
        return f"<{self.product.name} {self.prod_tech.name} {type(self)}>"

    @property
    def capacity(self) -> Decimal:
        return sum(self.needed_workers.values())  # type: ignore

    @property
    def efficient_shares(self) -> dict[Jobs, Decimal]:
        return {job: amount / self.capacity for job, amount in self.needed_workers.items()}

    def calc_efficiency(self) -> Decimal:
        """
        This method calculates the efficiency of production based on how well the proportion of the workers in the `Extractor` 
        object conform to the efficienct_share.

        Because of the nature of the algorithm used to calculate this, efficiency will always reach 0 when there are 0 workers
        or when there are double the workers needed for that particular job.
        """

        total_difference = D(0)

        for job, efficient_share in self.efficient_shares.items():
            share = self.workforce.get_share_of(job)
            difference = abs(efficient_share - share)
            weighted_difference = min(1, difference / efficient_share)

            total_difference += weighted_difference            

        mean_difference = total_difference / len(self.efficient_shares)
        efficiency = D(1) - mean_difference

        return efficiency

    @abstractmethod
    def produce(self) -> Stock:
        ...

    def calc_labor_demand(self) -> Commune:
        """ Returns a `dict[Jobs, int | float]` representing how many workers from a specific job are needed to fill up to capacity. """

        available_space = self.capacity - self.workforce.size
        labor_demand = CommuneFactory.create_by_job()

        if available_space <= 0: 
            return labor_demand

        for job, needed_pop in self.needed_workers.items():
            missing = max(D(0), needed_pop - self.workforce[job].size)
            labor_demand += PopFactory.job_makepop(job, missing)
        
        total_needed = labor_demand.size

        if total_needed < available_space:
            return labor_demand

        weights = {job: pop.size / total_needed for job, pop in labor_demand.items()}  # job will never be `tuple[Strata, Jobs.UNEMPLOYED]``
        labor_demand = CommuneFactory.create_by_job({job: weight * available_space for job, weight in weights.items()})  # type: ignore

        return labor_demand
    
    def can_employ(self, __value: Pop, /) -> bool:
        """ This method does not care about amounts, for excess amounts will just be left in the original `Pop` object. """

        labor_demand = self.calc_labor_demand()

        if __value.job != Jobs.UNEMPLOYED:
            raise CannotEmployError(f'Can only employ jobless pops, but {__value} was passed.')

        elif len(labor_demand[__value.stratum]) > D(0):
            return True
        
        else:
            return False

    def employ(self, pop: Pop, /) -> None:
        """ 
        Employs a pop assuming its job is `Jobs.UNEMPLOYED` and that the pop's stratum has jobs that are demanded by this `Extractor`.
        This modifies the passed `pop` argument in place. It removes the workers from it that were employed by this `Extractor`.
        """

        labor_demand = self.calc_labor_demand()
        job = max(labor_demand[pop.stratum].values()).job

        amount_employed = min(pop, labor_demand[job]).size
        self.workforce += PopFactory.job_makepop(job, amount_employed, pop.welfare)
        pop -= PopFactory.stratum_makepop(pop.stratum, amount_employed, pop.welfare)

    def is_unbalanced(self) -> bool:
        """ A `Extractor` object will attempt to unemploy all pops that are causing its efficiency to drop below 100%. """

        if any(self.workforce.get_share_of(job) > self.efficient_shares[job] for job in self.workforce):  # type: ignore
            return True
        
        else:
            return False

    def balance(self, alg: balance_alg, /) -> Commune:
        return alg(self)

    def fire_excess(self) -> Commune:
        """ Fires workers to bring the workforce back to the capacity. """

        overcapacity = self.workforce.size / self.capacity
        excess = CommuneFactory.create_by_job()

        for job, pop in self.workforce.items():
            amount = pop.size - pop.size / overcapacity
            excess += PopFactory.job_makepop(job, amount, pop.welfare)  # type: ignore

        self.workforce -= excess

        excess.unemploy_all()
        return excess

class Extractor(Industry):

    def produce(self) -> Stock:
        return create_stock({self.product: self.production.base_yield * self.workforce.size * self.calc_efficiency()})
        
class Manufactury(Industry):
    
    def __init__(self, product: Products,
                 prod_tech: Techs,
                 production: Technology,
                 needed_workers: dict[Jobs, Decimal],
                 workforce: Commune,
                 stockpile: Stock, /) -> None:
        
        super().__init__(product, prod_tech, production, needed_workers, workforce)
        self.stockpile = stockpile

    def calc_potential_production(self) -> Decimal:
        return self.production.base_yield * self.workforce.size * self.calc_efficiency()

    def calc_ceil(self) -> Decimal:
        potential_production = self.calc_potential_production()
        ceil = D(1)
        for product, share in self.production.recipe.items():
            needed_amount = share * potential_production
            ceil = min(self.stockpile[product].amount / needed_amount, ceil)
        
        return ceil
    
    def calc_input_demand(self) -> Stock:
        demand = create_stock()
        potential_production = self.calc_potential_production()

        for product, share in self.production.recipe.items():
            difference = potential_production * share - self.stockpile[product].amount

            try:
                demand[product] += create_good(product, difference)
            
            except NegativeAmountError:
                pass
                        
        return demand

    def produce(self) -> Stock:
        potential_production = self.calc_potential_production()
        ceil = self.calc_ceil()

        for product, share in self.production.recipe.items():
            amount_used = share * potential_production * ceil

            if isclose(amount_used, self.stockpile[product].amount):
                amount_used = self.stockpile[product].amount

            self.stockpile[product] -= create_good(product, amount_used)

        return create_stock({self.product: self.calc_potential_production() * ceil})

    def restock(self, stock: Stock) -> None:
        demand = self.calc_input_demand()

        for product, amount in demand.items():
            acquired = min(amount, stock[product])
            self.stockpile += acquired
            stock -= acquired

class IndustryFactory:

    @staticmethod
    def _validate_params(product: Products, prod_tech: Techs, needed_workers: pop_dict, /):
        if not isinstance(product, Products):
            raise TypeError
        
        if not isinstance(prod_tech, Techs):
            raise TypeError
        
        for key, val in needed_workers.items():
            if not isinstance(key, Jobs):
                raise TypeError
            
            if not isinstance(val, (int, float, str, Decimal)):
                raise TypeError
            
            needed_workers[key] = D(val)

            if needed_workers[key] < 0:  # type: ignore
                raise NegativeAmountError

    @classmethod
    def _create_extractor(cls,
                         product: Products,
                         needed_workers: pop_dict,
                         workforce: Optional[pop_dict] = None, /) -> Extractor:
        
        prod_tech = Techs.EXTRACTION
        cls._validate_params(product, prod_tech, needed_workers)
        production = product.techs[prod_tech]
        return Extractor(product, prod_tech, production, needed_workers, CommuneFactory.create_by_job(workforce))  # type: ignore
    
    @classmethod
    def _create_manufactury(cls,
                           product: Products,
                           prod_tech: Techs,
                           needed_workers: pop_dict,
                           workforce: Optional[pop_dict] = None,
                           stock: Optional[goods_dict] = None, /):
        
        cls._validate_params(product, prod_tech, needed_workers)
        production = product.techs[prod_tech]
        return Manufactury(product, prod_tech, production, needed_workers, CommuneFactory.create_by_job(workforce), create_stock(stock))  # type: ignore

    @overload
    @classmethod
    def create_industry(cls, product: Products, needed_workers: pop_dict, workforce: Optional[pop_dict] = None, /) -> Extractor:
        ...
    
    @overload
    @classmethod
    def create_industry(cls, 
                        product: Products, 
                        needed_workers: pop_dict, 
                        workforce: Optional[pop_dict], 
                        prod_tech: Techs, 
                        stock: Optional[goods_dict] = None, /) -> Manufactury:
        ...

    @classmethod
    def create_industry(cls,
                        product: Products,
                        needed_workers: pop_dict,
                        workforce: Optional[pop_dict] = None,
                        prod_tech: Techs = Techs.EXTRACTION,
                        stock: Optional[goods_dict] = None, /) -> Extractor | Manufactury:
        
        if prod_tech == Techs.EXTRACTION:
            return cls._create_extractor(product, needed_workers, workforce)
        
        else:
            return cls._create_manufactury(product, prod_tech, needed_workers, workforce, stock)

    def __init__(self, product: Products, needed_workers: pop_dict, prod_tech = Techs.EXTRACTION, /) -> None:
        if not isinstance(product, Products):
            raise TypeError(f'{type(product).__name__} type is not allowed in the `product` parameter.')
        
        if any(not isinstance(key, Jobs) or not isinstance(val, (int, float, str, Decimal)) for key, val in needed_workers.items()):
            raise TypeError(f'dict {needed_workers} does not conform to `pop_dict` type alias.')
                
        self.product = product
        self.needed_workers = needed_workers
        self.prod_tech = prod_tech

    @overload
    def __call__(self, workforce: Optional[pop_dict] = None, /) -> Extractor | Manufactury:
        ...
    
    @overload
    def __call__(self, workforce: Optional[pop_dict] = None, stock: Optional[goods_dict] = None, /) -> Manufactury:
        ...

    def __call__(self, workforce: Optional[pop_dict] = None, stock: Optional[goods_dict] = None, /) -> Extractor | Manufactury:
        return self.create_industry(self.product, self.needed_workers, workforce, self.prod_tech, stock)