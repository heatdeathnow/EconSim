from __future__ import annotations
from abc import ABC, abstractmethod
from utils import MethodLogger
from typing import Literal
from math import isclose
import variables as v
from typing import Optional

class Good:
    """
    The class is an abstraction of a real life resource such as iron, steel, oil or fruit.

    Parameters:
        name (`str`): what the resource is called.
        throughput (`int`): how many units of this resource one worker can produce at 100 efficiency.
        strata (`Literal["upper", "middle", "lower"]`): which strata can produce this resource.
        recipe (`dict[str, int]`): a dictionary mapping which resources are needed as inputs and how many, in order to produce
        this resource. A resource can have no recipe if this value is left as `None`.
    """

    def __init__(self, name: str, 
                 throughput: int, 
                 strata: Literal['upper', 'middle', 'lower'], 
                 recipe: dict[str, int] | None = None) -> None:
        
        self.name = name
        self.throughput = throughput  # How many units a worker produces at 100 efficiency.

        if strata.lower().strip() in ('upper', 'middle', 'lower'):
            self.strata = strata.lower().strip()  # Which strata can produce this resource.
        
        else:
            raise ValueError(f'The value passed in the parameter strata "{strata}" is not an acceptable strata.\n\
                             The only acceptable values are "upper", "middle" and "lower".')
        
        if recipe is None:
            self.recipe = None
        
        else:
            for resource in recipe:
                if resource not in v.GOODS:
                    raise ValueError(f'The resource "{resource}" does not exist.')

            self.recipe = recipe  # If this resource takes other resources as inputs in order to be produced.

v.GOODS = {
    'grain': Good('grain', 10, 'lower'), 
    'iron': Good('iron', 2, 'lower'),
}

class Industry(ABC, metaclass = MethodLogger if not v.TESTING else type):
    """
    This is an Abstract Class meant to be inherited by the Extractor and Manufactury concrete subclasses.

    This is a representation of a "Center of Production". This will mediate production between the provinces and its populations.

    The subclass Extractor is meant to represent the production of goods that take no other goods as intermediates.
    The subclass Manufactury is meant to represent the crafting of secundary goods, that take other goods to be crafted.

    Attributes:
        `produces` (`str`): the good produced by the object of one of the subclasses of `Industry`
        `biome` (`Biome`): the biome in which the industry is located. This affects how many goods are produced.
        `ideal_proportion` (`dict[str, float]`): a mapping of all the occupations this industry needs and their proportions to the total. (This will always add to 1.)
        `self.workers` `([str, Population])`: a mapping of all the occupations it needs and the Population objects working these occupations.
    """

    @abstractmethod
    def get_production(self) -> int:
        """
        This method produces a specific good specified in the objects `produces` attribute.

        The amount produced is determined by the `throughput` attribute of the specific good, the `advantage` attribute of the Biome object
        it's being produced in, the amount of workers producing the good and how close the proportion of workers is to the desired proportion.
        """

    def get_real_proportion(self) -> dict[str, float]:
        total = self.get_total_workers()

        try:
            real = {x: y.size / total for x, y in self.workers.items()}
        
        except ZeroDivisionError:
            # The other methods will understand they should keep this proportion as it and only raise the amount of workers if necessary.
            real = self.ideal_proportion

        return real

    def get_total_workers(self, strata: Optional[Literal['lower', 'middle', 'upper']] = None) -> int | float:
        total = 0

        for worker in self.workers.values():
            match strata:

                case None:
                    total += worker.size       

                case 'lower':
                    if isinstance(worker, LowerStrata):
                        total += worker.size 
                
                case 'middle':
                    if isinstance(worker, MiddleStrata):
                        total += worker.size 
                
                case 'upper':
                    if isinstance(worker, UpperStrata):
                        total += worker.size 

        return total

    def get_correct_sizes(self) -> dict[str, float]:
        """Given a reference occupation whose size is assumed to be correct, calculate all other sizes such that they are in a correct 
        proportion relative to the size who's assumed to be correct."""

        reference_occupation = max(self.workers, key = lambda occupation: self.workers[occupation].size)

        reference_size = self.workers[reference_occupation].size
        correct_size = {}
        for occupation in self.workers:
            if occupation == reference_occupation: continue

            #  reference occupation's proportion ------ size of reference (declared to be correct)
            #  desired proportion of a occupation ----- its correct size (to be calculated)
            #  
            # its correct size = (size of reference * desired proportion of a occupation) / reference occupation's proportion

            correct_size[occupation] = (reference_size * self.ideal_proportion[occupation]) / self.ideal_proportion[reference_occupation]

        return correct_size

    def get_fix_proportion(self) -> dict[str, float]:
        """
        Gets a labor demand that would fix the proportionality of an `Industry` object. First it declares that the largest occupation is in
        its correct size. Assuming that that size is correct, it calculates what all other sizes should be through the `get_correct_sizes`
        method. After this calculation, it subtracts the current size of each `Population` object from the size its suppose to be to get how
        many workers needs to be added to it.
        """

        proportion_demand: dict[str, float | int] = {}

        # Do not run all this performance-intensive code if you're already over capacity, or if there are no workers.
        total_workers = self.get_total_workers()
        if total_workers >= self.capacity or self.get_total_workers() <= 0:
            return proportion_demand

        correct_sizes = self.get_correct_sizes()
        if sum(correct_sizes.values()) > self.capacity:  # There won't be enough capacity to fix proportionaly, so get the best possible.
            available: list[str] = []

            for key, val in self.workers.items():
                if val.size < self.capacity * self.ideal_proportion[key]:
                    available.append(key)
                
                total_percentage = 0
                total_percentage += sum([self.ideal_proportion[occupation] for occupation in available])
                total_missing = self.capacity - total_workers

                for occupation in available:
                    adjusted_proportion = self.ideal_proportion[occupation] / total_percentage
                    proportion_demand[occupation] = total_missing * adjusted_proportion

            return proportion_demand
        
        else:
            for occupation, size in correct_sizes.items():
                difference = size - self.workers[occupation].size  # Should always be positive.

                if not isclose(difference, 0.0):
                    proportion_demand[occupation] = difference

        return proportion_demand

    def get_labor_demand(self, strata: Optional[Literal['lower', 'middle', 'upper']] = None) -> dict[str, float | int]:
        """
        Returns the labor demand of a `Industry` object. This takes into consideration both the amount of workers that would 
        be necessary to fix a disporportional workforce in an industry and the amount of workers necessary for each occupation
        in order for the industry to reach its capacity while not breaking proportionality.

        If there is no labor demand, returns an empty dictionary.
        """

        total_workers = self.get_total_workers()
        if total_workers >= self.capacity:
            return {}

        else:
            proportion_demand = self.get_fix_proportion()

            # Demand unrelated to proportionality. How many workers are needed to fill up to capacity.
            fill_up = max(self.capacity - (total_workers + sum(proportion_demand.values())), 0)

            labor_demand: dict[str, float] = {}
            for key, val in self.ideal_proportion.items():
                try:
                    total_for_occupation = proportion_demand[key] + (fill_up * val)

                    if total_for_occupation + total_workers > self.capacity:
                        total_for_occupation = self.capacity - total_workers
                
                except KeyError:
                    total_for_occupation = (fill_up * val)

                if not isclose(total_for_occupation, 0.0):
                    labor_demand[key] = total_for_occupation

            if strata is None:
                return labor_demand

            keys = list(labor_demand.keys())
            for key in keys:  # This is more inneficient than just calculating for just the wanted strata. TODO
                if ((   strata == 'lower'  and key not in LowerStrata.ALLOWED_OCCUPATIONS)
                    or (strata == 'middle' and key not in MiddleStrata.ALLOWED_OCCUPATIONS)
                    or (strata == 'upper'  and key not in UpperStrata.ALLOWED_OCCUPATIONS)):

                    del labor_demand[key]

            return labor_demand

    def get_goods_demand(self, stratum: Optional[v.Strata] = None) -> dict[str, float]:
        goods_demand: dict[str, float] = {}

        for population in self.workers.values():
            if (stratum is None
                or (stratum == v.Strata.LOWER and isinstance(population, LowerStrata))
                or (stratum == v.Strata.MIDDLE and isinstance(population, MiddleStrata))
                or (stratum == v.Strata.UPPER and isinstance(population, UpperStrata))): 

                consumption = population.get_consumption()

                for good, amount in consumption.items():
                    try:
                        goods_demand[good] += amount
                    
                    except KeyError:
                        goods_demand[good] = amount
        
        return goods_demand

    def grow(self, stockpile: dict[str, float | int]) -> None:
        upper_types = 0
        middle_types = 0
        lower_types = 0
        for worker_type in self.ideal_proportion:
            if worker_type in UpperStrata.EXISTING_OCCUPATIONS:
                upper_types += 1
            
            elif worker_type in MiddleStrata.EXISTING_OCCUPATIONS:
                middle_types += 1
            
            elif worker_type in LowerStrata.EXISTING_OCCUPATIONS:
                lower_types += 1
            
            else:
                raise TypeError(f'{worker_type} is not in any of the strata\'s allowed occupations')
        
        priority = [UpperStrata, MiddleStrata, LowerStrata]
        upper = self.get_goods_demand(v.Strata.UPPER)
        middle = self.get_goods_demand(v.Strata.MIDDLE)
        lower = self.get_goods_demand(v.Strata.LOWER)

        for stratum in priority:
            for worker in self.workers.values():
                if isinstance(worker, stratum):
                    consumption = worker.get_consumption()
                    share = {good: min([consumption[good], amount / upper_types]) for good, amount in stockpile.items()}
                    welfare = worker.get_welfare(share, consumption)
                    worker.get_change(welfare)



        ...

    def distribute_workers(self, *populations: UpperStrata | MiddleStrata | LowerStrata) -> None:
        """
        This method takes in a `list` of one or several strata objects and distributes it to the occupations that are in need 
        of workers in the industry object.

        If one of the strata passed does not perform one of the needed occupations, it will raise a ValueError.
        """

        labor_demand = self.get_labor_demand()
        
        for strata in populations:
            if strata.occupation in labor_demand:
                if strata.size > labor_demand[strata.occupation]:
                    v.logger.warning(f"""A {strata.occupation} `{type(strata).__name__}` object with a size of {strata.size} has been passed to a
                                     `{type(self).__name__}` object despite its {strata.occupation} demand of only {labor_demand[strata.occupation]}.""")

                self.workers[strata.occupation] += strata  # type: ignore

                if self.workers[strata.occupation].size < 0:
                    raise ValueError(f"""The strata of size {strata.size} was passed to a `{type(self)}` object, causing its size to go negative.
    Info:
        Object: {self}.
        Strata: {strata}""")

            else:
                raise ValueError(f"""A Population object performing the "{strata.occupation}" occupation 
    has been passed to the `distribute_workers` method of a `{type(self).__name__}` object
    despite this object having no use for this occupation.""")

    def __init__(self, 
                 produces: str, 
                 biome: Biome, 
                 capacity: float,
                 needed_occupations: dict[str, float], 
                 populations: tuple[UpperStrata | MiddleStrata | LowerStrata, ...] | None = None) -> None:

        # PRODUCES
        if produces in v.GOODS:
            self.produces = produces

        else:
            raise ValueError(f'The non-existant "{produces}" good was passed in the creation of a {type(self).__name__} object.')
        
        # BIOME
        from terrain import Biome
        if isinstance(biome, Biome):
            self.biome = biome
        
        else:
            raise TypeError(f'The argument {biome} of type {type(biome)} passed at the `biome` parameter is not an instance of the `Biome` class.')
        
        # CAPACITY
        if isinstance(capacity, (int, float)) and capacity > 0:
            self.capacity = capacity
        
        elif isinstance(capacity, (int, float)):
            raise ValueError(f"""An `Industry` object cannot have a capacity that is lesser than 0. Value passed: {capacity}""")
        
        else:
            raise TypeError(f"""The parameter `capacity` for the `Industry` class can only be `int` or `float`,
                            but a value of {capacity} of type {type(capacity)} was passed.""")

        # IDEAL_PROPORTION
        if isclose(sum(needed_occupations.values()), 1.0):
            self.ideal_proportion = needed_occupations
        
        else:
            raise ValueError(f"""The ideal proportion of the occupations does not add up to 100%.
                             Variables:
                                values passed: {needed_occupations}.
                                sum of their values: {sum(needed_occupations.values())}""")

        # WORKERS
        self.workers: dict[str, Population] = {occupation: None for occupation in needed_occupations}  # Initializes the workers dicionary with all needed occupations.
        if populations:  # Distributes the workers, if they have been passed at instantiation.
            for occupation in needed_occupations:
                if occupation not in Population.EXISTING_OCCUPATIONS:
                        raise ValueError(f'The non-existant "{occupation}" occupation was passed in the creation of a `{type(self).__name__}` object.')
                
                for population in populations:
                    try:
                        self.workers[population.occupation] = population  # type: ignore
                    
                    except KeyError:
                        raise KeyError(f"""A strata object performing the "{population.occupation}" occupation has been passed to a
                                       `{type(self).__name__}` object despite it having no need for it.
                                       Information:
                                           Occupations needed: {[x for x in needed_occupations]}.""")

        if None in self.workers.values():  # This allows the user to pass some but not all of the needed workers at instantiation.
            for key, val in self.workers.items():
                if val is None:
                    if key in LowerStrata.ALLOWED_OCCUPATIONS:
                        self.workers[key] = LowerStrata(size = 0, occupation = key)

                    elif key in MiddleStrata.ALLOWED_OCCUPATIONS:
                        self.workers[key] = MiddleStrata(size = 0, occupation = key)

                    elif key in UpperStrata.ALLOWED_OCCUPATIONS:
                        self.workers[key] = UpperStrata(size = 0, occupation = key)

    def __str__(self) -> str:
        workers = {x: y.size for x, y in self.workers.items()}
        text = f"""<{type(self).__name__} object>
produces: {self.produces}
capacity: {self.capacity}
ideal_proportion: {self.ideal_proportion}
workers: {workers}
real_proportion: {self.get_real_proportion()}
"""

        return text
        
class Extractor(Industry, metaclass = MethodLogger if not v.TESTING else type):
    def get_production(self) -> float:
        """
        Because of the way the formula works. If more than 50% of a occupation is needed and there are none
        of these workers, nothing will be produced.
        """

        good = self.produces
        real_proportion = self.get_real_proportion()
        difference = 0.0

        for real, ideal in zip(real_proportion.values(), self.ideal_proportion.values()):

            # Since both proportions sum to 1, division is unnecessary.
            difference += abs(ideal - real)

        efficiency = max(1 - difference, 0.0)

        # The amount of goods extracted from the earth is equal to the sum of the workers times the biome advantage times the good's throughput
        # times the a number from 0 to 1 depending on how close the Extractor's populations match the ideal.
        goods_produced = self.get_total_workers() * self.biome.advantage[good] * v.GOODS[good].throughput * efficiency
        return goods_produced

    def __init__(self, produces: str, biome: Biome, capacity: float, needed_occupations: dict[str, float], populations: tuple[UpperStrata | MiddleStrata | LowerStrata, ...] | None = None) -> None:
        super().__init__(produces, biome, capacity, needed_occupations, populations)

class Manufactury(Industry): pass


# These are just for annotations, so they are placed at the very bottom to prevent circular importing.
from population import *
from terrain import *
