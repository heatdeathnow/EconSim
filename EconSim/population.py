from __future__ import annotations
from abc import ABC, abstractmethod
from utils import MethodLogger
from typing import Self
import variables as v

class Population(ABC, metaclass = MethodLogger if not v.TESTING else type):
    """
    This Abstract Class mirrors Victoria 2's pops. A population will be either upper, middle or lower strata.

    All strata subclasses inheret from this class. This base class should *not* be used.

    Attributes:
        size (int): Represents the amount of people in the Population object.
        culture (str): This group of people's specific culture. E.g. French, Brazilian, Bantu etc.
    
    Methods:
        change(stockpile: int): Takes in the province's stockpile and returns the population change.
    """

    EXISTING_OCCUPATIONS = ['Farmer', 'Miner', 'Laborer', 
                            'Artisan', 'Bureaucrat', 'Specialist',
                            'Capitalist', 'Official']

    def get_welfare(self, stockpile: dict[str, int], consumption: dict[str, int]) -> float:
        """
        This method is responsible for calculating the population's welfare based on the province's stockpile.
        
        That is, how well it's doing. The welfare is calculated using the Province object's stockpile. If all the needs of the 
        population are fulfilled this method will return 1. If none of the needs are fulfilled it will return 0. If some but not
        all are fulfilled, it will return a number between 0 and 1.
        """

        self.needs: dict[str, int]
        if not hasattr(self, 'needs'):
            raise AttributeError(f'Subclass {type(self).__name__} lacks the `needs` attribute.')
        
        else:
            welfare = 0.0

            for resource, amount in consumption.items():
                try:
                    if amount <= 0: continue
                    welfare += min(1, stockpile[resource] / consumption[resource])
                
                except KeyError:
                    raise KeyError(f'The resource "{resource}" was not in the stockpile.')
            
            welfare /= len(self.needs)
            return welfare

    def get_consumption(self) -> dict[str, int | float]:
        """
        Returns a mapping of all resources and how much of them this Population object consumed.

        The formula is: how much of these resource are needed for one person * the amount of people.
        """

        self.needs: dict[str, int]
        consumption = {key: val * self.size for key, val in self.needs.items()}

        if any([x < 0 for x in consumption.values()]):
            raise ValueError(f"""Got a negative amount when calculating consumption for a `{type(self).__name__}` object.
Information:
    `{type(self).__name__}`'s `needs` attribute: {self.needs}
    `{type(self).__name__}`'s `size` attribute: {self.size}
    `consumption`: {consumption}""")
            
        return consumption

    @abstractmethod
    def get_change(self, welfare: float) -> tuple[Population, ...]:
        """
        This abstract method has its implementation in all base classes.

        This method talkes in a welfare value (should be a number 0.0 to 1.0) and returns a tuple containing subclasses of the Population class.

        UpperStrata objects may return either a tuple[UpperStrata] or a tuple[MiddleStrata].
        MiddleStrata objects may return either tuple[UpperStrata, MiddleStrata], or a tuple[MiddleStrata], tuple[LowerStrata].
        LowerStrata objects may return either a tuple[MiddleStrata, LowerStrata] or a tuple[LowerStrata] of either negative or positive size.
        """

        if welfare > 1 or welfare < 0:
            raise ValueError(f'`{type(self).__name__}` object\'s `get_change` method has received a welfare value greater than 1 or lesser than 0.\n \
                             welfare received: {welfare}')

    def __init__(self, size: int | float, occupation: str | None = None) -> None:
        self.size = size  # Number of people.

        if occupation is None:
            self.occupation = None

        elif occupation in type(self).ALLOWED_OCCUPATIONS:  # type: ignore
            self.occupation = occupation
        
        elif occupation in Population.EXISTING_OCCUPATIONS:
            raise ValueError(f"""The occupation "{occupation}" isn\'t allowed for a `{type(self).__name__}` object.""")
        
        else:
            raise ValueError(f"""The occupation "{occupation}" does not exist or is not yet implemented.""")
        
        self.culture = NotImplemented

    def __add__(self, __value: Population | int | float) -> Population:
        if isinstance(__value, (int, float)):

            # Kudos to Chat GPT for this ingenious solution. I had never called a function and then its result in the same line.
            return type(self)(self.size + __value, self.occupation)

        elif not isinstance(__value, type(self)):
            raise TypeError(f'The of addition of a {type(self).__name__} object and a {type(__value).__name__} object is not defined.')
        
        elif self.culture != __value.culture:
            raise TypeError(f'The addition of two {type(self)} objects with different cultures is not allowed.')
        
        elif self.occupation != __value.occupation:
            raise TypeError(f"""The addition of two {type(self)} objects with different occupations is not allowed""")

        else:
            return type(self)(self.size + __value.size, self.occupation) 
    
    def __radd__(self, __value: Population | int | float) -> Population:
        if isinstance(__value, (int, float)):
            return type(self)(__value + self.size, self.occupation)
        
        elif not isinstance(__value, type(self)): 
            raise TypeError(f'The of addition of a {type(self).__name__} object and a {type(__value).__name__} object is not defined.')

        elif self.culture != __value.culture:
            raise TypeError(f'The addition of two {type(self)} objects with different cultures is not allowed.')
        
        elif self.occupation != __value.occupation:
            raise TypeError(f"""The addition of two {type(self)} objects with different occupations is not allowed""")

        else:
            return type(self)(__value.size + self.size, self.occupation) 

    def __iadd__(self, __value: Population | int | float) -> Self:
        if isinstance(__value, (int, float)):
            self.size += __value
        
        elif not isinstance(__value, type(self)):
            raise TypeError(f'The of addition of a {type(self).__name__} object and a {type(__value).__name__} object is not defined.')
        
        elif self.culture != __value.culture:
            raise TypeError(f'The addition of two {type(self)} objects with different cultures is not allowed.')
        
        elif self.occupation != __value.occupation:
            raise TypeError(f"""The addition of two {type(self)} objects with different occupations is not allowed""")

        else:
            self.size += __value.size

        return self
    
    def __sub__(self, __value: Population | int | float) -> Population:
        if isinstance(__value, (int, float)):
            return type(self)(self.size - __value, self.occupation)
        
        elif not isinstance(__value, type(self)):
            raise TypeError(f'The subtraction of a {type(self).__name__} object and a {type(__value).__name__} object is not defined.')
        
        elif self.culture != __value.culture:
            raise TypeError(f'The subtraction of two {type(self)} objects with different cultures is not allowed.')
        
        elif self.occupation != __value.occupation:
            raise TypeError(f"""The subtraction of two {type(self)} objects with different occupations is not allowed""")

        else:  # If they're both objects of the same strata and have the same culture.
            return type(self)(self.size - __value.size, self.occupation)
    
    def __rsub__(self, __value: Population | int | float) -> Population:
        if isinstance(__value, (int, float)):
            return type(self)(__value - self.size, self.occupation)
        
        elif not isinstance(__value, type(self)): 
            raise TypeError(f'The of addition of a {type(self).__name__} object and a {type(__value).__name__} object is not defined.')

        elif self.culture != __value.culture:
            raise TypeError(f'The addition of two {type(self)} objects with different cultures is not allowed.')
        
        elif self.occupation != __value.occupation:
            raise TypeError(f"""The addition of two {type(self)} objects with different occupations is not allowed""")

        else:
            return type(self)(__value.size - self.size, self.occupation) 

    def __isub__(self, __value: Population | int | float) -> Self:
        if isinstance(__value, (int, float)):
            self.size -= __value
        
        elif not isinstance(__value, type(self)):
            raise TypeError(f'The of subtraction of a {type(self).__name__} object and a {type(__value).__name__} object is not defined.')
        
        elif self.culture != __value.culture:
            raise TypeError(f'The subtraction of two {type(self)} objects with different cultures is not allowed.')
        
        elif self.occupation != __value.occupation:
            raise TypeError(f"""The subtraction of two {type(self)} objects with different occupations is not allowed""")

        else:
            self.size -= __value.size
        
        return self

    def __eq__(self, __value: Population) -> bool:
        if not isinstance(__value, type(self)):
            return False
        
        elif self.size != __value.size:
            return False
        
        elif self.occupation != __value.occupation:
            return False
        
        elif self.culture != __value.culture:
            return False
        
        else:
            return True

    def __repr__(self) -> str:
        return f'<{type(self).__name__}, size: {self.size}, occupation: {self.occupation}>'

class UpperStrata(Population):

    ALLOWED_OCCUPATIONS = ['Capitalist', 'Official']

    def get_change(self, welfare: float) -> tuple[Population, ...]:
        super().get_change(welfare)
        
        if welfare < self.welfare_threshold:
            return (MiddleStrata(self.size * self.demotion_rate, None), )
        
        else:
            return (UpperStrata(self.size * self.growth_rate, self.occupation), )

    def __init__(self, size: int | float, occupation: str | None = None) -> None:
        super().__init__(size, occupation)

        self.needs = {'grain': 6, 'iron': 3}
        self.welfare_threshold = 0.85
        self.growth_rate = 0.01
        self.demotion_rate = 0.05

class MiddleStrata(Population):

    ALLOWED_OCCUPATIONS = ['Artisan', 'Bureaucrat', 'Specialist']

    def get_change(self, welfare: float) -> tuple[Population, ...]:
        super().get_change(welfare)

        if welfare < self.welfare_threshold:
            return (LowerStrata(self.size * self.demotion_rate, None), )
        
        elif self.promote_threshold > welfare >= self.welfare_threshold:
            return (MiddleStrata(self.size * self.growth_rate, self.occupation), )

        else:
            return (UpperStrata(self.size * self.promotion_rate, None), MiddleStrata(self.size * self.growth_rate, self.occupation), )

    def __init__(self, size: int | float, occupation: str | None = None) -> None:
        super().__init__(size, occupation)

        self.needs = {'grain': 2, 'iron': 1}
        self.welfare_threshold = 0.75
        self.promote_threshold = 0.95
        self.growth_rate = 0.03
        self.promotion_rate = 0.01
        self.demotion_rate = 0.03

class LowerStrata(Population):

    ALLOWED_OCCUPATIONS = ['Farmer', 'Miner', 'Laborer']

    def get_change(self, welfare: float) -> tuple[Population, ...]:
        super().get_change(welfare)

        if welfare < self.welfare_threshold:
            return (LowerStrata(-self.size * self.decline_rate, self.occupation), )
        
        elif self.promote_threshold > welfare >= self.welfare_threshold:
            return (LowerStrata(self.size * self.growth_rate, self.occupation), )
        
        else:
            return (MiddleStrata(self.size * self.promotion_rate, None), LowerStrata(self.size * self.growth_rate, self.occupation), )
    
    def __init__(self, size: int | float, occupation: str | None = None) -> None:
        super().__init__(size, occupation)

        self.needs = {'grain': 1}
        self.welfare_threshold = 0.5
        self.promote_threshold = 0.9
        self.growth_rate = 0.05
        self.decline_rate = 0.01
        self.promotion_rate = 0.03
