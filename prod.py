from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence
from goods import Goods, Stockpile
from pop import Jobs, Pop, pop_factory

class Extractor:

    THROUGHPUT = 1.25  # This is a placeholder value while the feature does not yet exist.

    def __init__(self, product: Goods, workforce: Workforce) -> None:
        self.product = product
        self.workforce = workforce
    
    def link_stockpile(self, stockpile):
        self.stockpile = stockpile

    def produce(self) -> Stockpile:
        return Stockpile({self.product: Extractor.THROUGHPUT * self.workforce.size * self.workforce.efficiency})
    
@dataclass
class Workforce:
    needed: dict[Jobs, int | float]
    pops: dict[Jobs, Pop]

    def link_stockpile(self, stockpile: Stockpile) -> None:
        self.stockpile = stockpile

    @property
    def nominal_goods_demand(self) -> Stockpile:
        """
        What and how many goods this workforce would need assuming it has an empty stockpile.
        """
    
        demand = Stockpile()

        for pop in self.pops.values():
            for good, amount in pop.consumption.items():
                demand[good] += amount
        
        return demand

    @property
    def effective_goods_demand(self) -> Stockpile:
        """
        What and how many goods this workforce needs considering the ones available in the Stockpile.
        """

        demand = Stockpile()

        for good, amount in self.nominal_goods_demand.items():
            if self.stockpile[good] < amount:
                demand[good] += amount - self.stockpile[good]
        
        return demand

    def labor_demand(self) -> dict[Jobs, int | float]:
        """
        Returns a dictionary of `Jobs` members and `int | float` pairs representing how many workers from a specific job are
        needed to fill up to capacity.
        """

        if self.size >= self.capacity:
            return {}

        calibrate = .0  # If somehow the Workforce has gotten more workers than it needs, calibration will be needed.
        demand: dict[Jobs, int | float] = {}
        for job, pop in self.pops.items():
            if self.needed[job] > pop.size:
                demand[job] = self.needed[job] - pop.size
            
            elif self.needed[job] < pop.size:
                calibrate += pop.size - self.needed[job]
        
        if calibrate > .0:  # This prevents a `Workforce` demanding more workers than it has the capacity for.
            for job, amount in demand.copy().items():
                corrected_amount = max(0, amount - calibrate)

                if corrected_amount == 0:
                    del demand[job]
                
                else:
                    demand[job] = corrected_amount

        return demand

    @property
    def efficiency(self) -> float:
        """
        Efficiency is the measurement of how well the workforce compares to the needed pops.
        
        This is calculated as the mean of the differences of the needed workers and the amount it has, or the mean of A / B
        such that A / B is strictly less than or equal to one.
        """

        total_difference: float = len(self.needed)

        for job, pop in self.pops.items():
            difference = abs(self.needed[job] - pop.size)
            ratio = min(1, difference  / self.needed[job])  # Capping it at one prevents negative efficiencies.
            total_difference -= ratio
        
        efficiency = total_difference / len(self.needed)
        return efficiency
    
    @property
    def size(self) -> int | float:
        return sum([pop.size for pop in self.pops.values()])

    def __post_init__(self) -> None:
        self.capacity = sum([value for value in self.needed.values()])

def workforce_factory(needed: dict[Jobs, float | int], stockpile: Stockpile, pops: Optional[Sequence[Pop]] = None) -> Workforce:
    for job, amount in needed.items():
        if job not in Jobs:
            raise TypeError(f'{job} is not a member of the `Jobs` `Enum`.')
        
        if not isinstance(amount, (int, float)):
            raise TypeError(f'{amount} is not int or float.')
        
        if amount <= 0:
            raise ValueError(f'`needed` dictionary of `Jobs` enum members must have all positive values.')
    
    if not isinstance(stockpile, Stockpile):
        raise TypeError(f'{stockpile} is not a `Stockpile` object.')
    
    total_size = 0.0
    pops_arg = {job: pop_factory(0, stockpile, job) for job in needed}
    if pops:
        for pop in pops:
            if not isinstance(pop, Pop):
                raise TypeError(f'{pop} is not a `Pop` object.')
    
            if pop.job is None:
                raise ValueError(f'`Workforce` object cannot have idle pops.')

            if pop.job not in needed:
                raise ValueError(f'{pop}\'s job is not needed in {needed}.')
        
            pops_arg[pop.job] += pop
            total_size += pop.size
    
    if total_size > sum([size for size in needed.values()]):
        raise ValueError('Cannot have total size of `Pop`\'s passed over capacity.')
        
    workforce = Workforce(needed, pops_arg)
    workforce.link_stockpile(stockpile)
    return workforce

def extractor_factory(workforce: Workforce, product: Goods, stockpile: Stockpile) -> Extractor:
    
    if not isinstance(workforce, Workforce):
        raise TypeError(f'`workforce` argument must be a `Workforce` object.')

    if product not in Goods:
        raise TypeError(f'`product` argument must be a member of the `Goods` enum.')

    if not isinstance(stockpile, Stockpile):
        raise TypeError(f'{stockpile} is not a `Stockpile` object.')
    
    extractor = Extractor(product, workforce)
    extractor.link_stockpile(stockpile)
    extractor.workforce.link_stockpile(extractor.stockpile)
    return extractor
