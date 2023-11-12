from __future__ import annotations
import variables as v
from math import isclose
from utils import MethodLogger
from population import Population, LowerStrata, MiddleStrata, UpperStrata
from production import Industry, Extractor, Manufactury
from typing import Literal

class Biome:
    """
    Biomes with different resources and living conditions.

    While mountainous biomes can be rich in minerals, the living conditions there are difficult.

    Attributes:
        `name` (`str`): The biome's name.

        `efficiency` (`dict[str, int]`): A mapping of every resource and the biome's efficiency in relation to them. This is a 
        number from 0.0 to infinity, with 1.0 meaning the biome has normal efficiency for this good. The higher the number, the better
        the production. An advantage of 2.0 means twice as many goods can be produced in this province compared to others. 
    """

    def __init__(self, name: str, **kwargs: int | float) -> None:
        self.name = name
        self.advantage = {x: 1.0 for x in v.GOODS}  # All resources default to normal efficiency.

        for key, val in kwargs.items():
            if key in v.GOODS:  # Checks if the good actually exists.
                self.advantage[key] = val  # Sets the efficiency to the user-passed value.

            else:
                raise ValueError(f'The good "{key}" does not exist or has not yet been implemented.')

class Province(metaclass = MethodLogger if not v.TESTING else type):
    
    """
    A place in the World with resources, production centers, and populations.

    Attributes:
        name (`str`): The provinces name. Example: London.
        biome (`Biome`): The province's biome of sorts. Determines resource efficiency. Example: hills, fields.
        industries (`Industry`): The production centers present within this province. This is the only way to produce goods.
        stockpile (`dict[str, int]`): A mapping of the name of every good that exists and the amount that this province has stockpiled.
        idle_pops (`dict[str, Population]`): A mapping of the "upper", "middle", "lower" keys and the respective idle population of these
    strata's objects.
    """

    def distribute_idle_pops(self) -> None:
        """
        Distribute all the workers in its `idle_workers` dictionary to its industries that are in demand for labor.
        """
        
        strata_needs = {stratum.value: 0 for stratum in v.Strata}
        for industry in self.industries.values():
            for stratum in v.Strata:
                if industry.get_labor_demand(stratum.value):
                     strata_needs[stratum.value] += 1

        if not any(strata_needs.values()): return
        
        per_industry = {stratum.value: 0.0 for stratum in v.Strata}
        for stratum in v.Strata:
            try:
                per_industry[stratum.value] = self.get_total_idle_pops(stratum.value) / strata_needs[stratum]

            except ZeroDivisionError:
                per_industry[stratum.value] = 0.0

        for industry in self.industries.values():
            for stratum in v.Strata:
                demands = industry.get_labor_demand(stratum.value)
                total_demand = sum(list(demands.values()))
                left = self.get_total_idle_pops(stratum.value)

                if min(left, per_industry[stratum.value]) < total_demand:
                    for occupation, amount in demands.items():
                        available = min(left, per_industry[stratum.value]) * (amount / total_demand)

                        match stratum:
                            case v.Strata.LOWER:
                                pop = LowerStrata(available, occupation)
                            
                            case v.Strata.MIDDLE:
                                pop = MiddleStrata(available, occupation)
                            
                            case v.Strata.UPPER:
                                pop = UpperStrata(available, occupation)
                        
                        industry.distribute_workers(pop)
                
                else:  # It gets everything it wants.
                    match stratum:
                        case v.Strata.LOWER:
                            industry.distribute_workers(*[LowerStrata(amount, occupation) for occupation, amount in demands.items()])
                        
                        case v.Strata.MIDDLE:
                            industry.distribute_workers(*[MiddleStrata(amount, occupation) for occupation, amount in demands.items()])
                        
                        case v.Strata.UPPER:
                            industry.distribute_workers(*[UpperStrata(amount, occupation) for occupation, amount in demands.items()])

    def get_total_idle_pops(self, strata: Literal[None, 'lower', 'middle', 'upper'] = None) -> float | int:
        total = 0

        if strata is None:
            for pop in self.idle_pops.values():
                total += pop.size
            
            return total
        
        try:
            return self.idle_pops[strata].size
        
        except KeyError:
            raise KeyError(f'{strata} was passed to a `get_total_idle_pops` method.')

    def get_total_pops(self, strata: Literal[None, 'lower', 'middle', 'upper'] = None) -> float | int:
        total = self.get_total_idle_pops(strata)

        for industry in self.industries.values():
            for occupation, population in industry.workers.items():
                if (strata is None 
                    or (strata == 'lower'  and occupation in LowerStrata.ALLOWED_OCCUPATIONS)
                    or (strata == 'middle' and occupation in MiddleStrata.ALLOWED_OCCUPATIONS)
                    or (strata == 'upper'  and occupation in UpperStrata.ALLOWED_OCCUPATIONS)):
                    total += population.size

        return total

    def get_total_labor_demand(self) -> dict[str, float | int]:
        """
        Adds together all the labor demands of the `Province` object's industries.
        """

        total_labor_demand: dict[str, float | int] = {}
        for industry in self.industries.values():
            labor_demand = industry.get_labor_demand()

            for occupation, need in labor_demand.items():
                try:
                    total_labor_demand[occupation] += need
            
                except KeyError:
                    total_labor_demand[occupation] = need
        
        return total_labor_demand

    def get_output(self) -> dict[str, float]:
        goods_produced = {}

        for key, val in self.industries.items():
            try:
                goods_produced[key] += val.get_production()
            
            except KeyError:
                produced = val.get_production()

                if not isclose(produced, 0.0):
                    goods_produced[key] = val.get_production()

        return goods_produced

    def grow(self) -> None:
        lower = self.get_total_pops('lower')
        middle = self.get_total_pops('middle')
        upper = self.get_total_pops('upper')

        
        ...

    def __init__(self, 
                 name: str, 
                 biome: Biome,
                 industries: dict[str, Extractor | Manufactury],
                 stockpile: dict[str, int] | None = None,
                 *populations: UpperStrata | MiddleStrata | LowerStrata) -> None:
        
        """
        The attribute `idle_pops` shall only house population objects whose `occupation` has been set to `None`. If a population has been passed
        to it in initialization and it is not of `None` `occupation`, then it will be set to `None`. Only when assigning workers to industries
        shall they gain a `occupation`. With this in mind, the `idle_pops` attribute needs to be either a dictionary or a dataclass, and it
        needs to contain three keys "lower", "middle", and "upper".
        """
        from population import Population, LowerStrata, MiddleStrata, UpperStrata

        self.name = name
        self.biome = biome

        self.industries: dict[str, Industry] = {}
        for key, val in industries.items():
            if key not in v.GOODS:
                raise ValueError(f'The good "{key}" does not exist or has not yet been implemented.')
            
            elif not issubclass(type(val), Industry):
                raise TypeError(f'The object `{type(val).__name__}` is not a subclass of the `Industry` superclass.')

            else:
                self.industries[key] = val
        
        self.stockpile = {x: 0 for x in v.GOODS}
        if stockpile is not None:
            for key, val in stockpile.items():  
                if key in v.GOODS:  # Checks if the good is actually implemented 
                    self.stockpile[key] = val
                
                else:
                    raise ValueError(f'The good {key} does not exist or has not yet been implemented.')
        
        # If something that is not a subclass of the Population superclass has been passed at the populations parameter...
        self.idle_pops: dict[str, LowerStrata | MiddleStrata | UpperStrata] = {
            'lower': LowerStrata(0),
            'middle': MiddleStrata(0),
            'upper': UpperStrata(0),
        }
        if populations:
            for population in populations:
                if not issubclass(type(population), Population):
                    raise TypeError(f"""The object {population} has been passed to a `Province` object's `populations` parameter
                                    despite this parameter only accepting subclasses of the `Population` superclass.""")

                if population.size < 0:
                    raise ValueError(f"""Size of population must be positive: {population}.""")

                if population.occupation is not None:
                    population.occupation = None
                
                match type(population):
                    case x if x is LowerStrata:
                        self.idle_pops['lower'] += population
                    
                    case x if x is MiddleStrata:
                        self.idle_pops['middle'] += population
                    
                    case x if x is UpperStrata:
                        self.idle_pops['upper'] += population

    def __str__(self) -> str:
        idle_pops = {x: y.size for x, y in self.idle_pops.items()}

        text = f"""<{type(self).__name__} object>
biome: {self.biome.name}
industries: {[x for x in self.industries]}
idle_pops: {idle_pops}"""
        
        return text

v.BIOMES = {
    'field': Biome('field', grain = 1.2, iron = 1.0), 
    'hill': Biome('hill', grain = .6, iron = 1.1)
}
