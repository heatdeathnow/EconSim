from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Self
from prod import Goods, Stockpile
from enum import Enum, auto
from math import isclose

class Strata(Enum):
    LOWER = auto()
    MIDDLE = auto()
    UPPER = auto()

class Jobs(Enum):
    FARMER = auto()
    MINER = auto()
    SPECIALIST = auto()

@dataclass
class Pop:
    """
    ### This dataclass represents a population.

    Do not instantiated this class manually! Use `pop_factory`.
    
    #### Parameters:
        - `stratum`: One of the stratum enumerated in the `Strata` `Enum`; e.g.: `Strata.LOWER`.
        - `size`: The amount of people in this specific population - can be a `float` or an `int`.
        - `job`: One of the jobs in the `Jobs` `Enum`. Stratas have jobs specific to them and cannot have jobs from another stratum.
        - `stockpile`: A `Stockpile` object from the `prod` module. If nothing is passed, an empty stockpile is used.
    
    #### Additional attributes:
        - `promotes`: The stratum from the `Strata` `Enum` that this object's stratum promotes to; or `None` if does not promote.
    e.g.: `Strata.LOWER` promotes to `Strata.MIDDLE`.

    #### Properties:
        - `consumption`: A `dict[Goods, float | int]` mapping the goods this `Pop` object needs and their respective needed amounts.
    `Goods` is a `Enum` member from the `Goods` `Enum` in the `prod` module. Each stratum has different needs and respective amounts.
        
        - `welfare`: A `float` ranging from 0.0 to 1.0 expressing how much of their needs this `Pop` object is capable of consuming.
    """

    JOBS = {
        Strata.LOWER: tuple([Jobs.FARMER, Jobs.MINER]),
        Strata.MIDDLE: tuple([Jobs.SPECIALIST, ]),
        # Strata.UPPER: tuple()
    }

    NEEDS = {
        Strata.LOWER: {Goods.WHEAT: 1.0},
        Strata.MIDDLE: {Goods.WHEAT: 2.0, Goods.IRON: 1.0},
        # Strata.UPPER: {}
    }

    WELFARE_THRESHOLD = 0.75  # Pops with a welfare higher than or equal to this value will grow and promote, otherwise decline.
    GROWTH_RATE = 0.05  # It will grow by 5 people per 100 people.
    PROMOTE_RATE = 0.01  # It will promote by 1 person per 100 people.

    stratum: Strata
    size: int | float
    job: Optional[Jobs] = None
    stockpile: Stockpile = field(default_factory=Stockpile)

    @property
    def consumption(self) -> dict[Goods, int | float]:
        return {good: need * self.size for good, need in Pop.NEEDS[self.stratum].items()}

    @property
    def welfare(self) -> float:

        if isclose(self.size, 0.0):  # This prevents ZeroDivisionError
            return 0.0

        welfare = 0.0

        for good, amount in self.consumption.items():
            try:
                welfare += min([1, self.stockpile[good] / amount])
            
            except KeyError:
                continue

        welfare /= len(Pop.NEEDS[self.stratum])
        return welfare

    def tick(self) -> Optional[Pop]:
        """
        Represents "one round" of the simulation for this `Pop` object or one `tick`.

        Grows or shrinks the size of the `object` 
        and optionally returns another `Pop` object if the object's `promotes` attribute is not `None`
        """

        welfare = self.welfare
        original_size = self.size

        for good, amount in self.consumption.items():
            self.stockpile[good] -= min([Pop.NEEDS[self.stratum][good] * self.size, amount])

        if welfare >= Pop.WELFARE_THRESHOLD:
            self += self.size * Pop.GROWTH_RATE

            if self.promotes:
                return pop_factory(original_size * Pop.PROMOTE_RATE, stratum = self.promotes)
            
        else:
            self -= self.size * Pop.GROWTH_RATE

    def __post_init__(self) -> None:
        match self.stratum:
            case Strata.LOWER:
                self.promotes = Strata.MIDDLE
            
            case _:
                self.promotes = None

    def __str__(self) -> str:
        if self.job is None:
            return f'<{self.stratum.name, self.size}>'
        
        else:
            return f'<{self.job.name}: {self.size}>'

    def __iadd__(self, __value: float | int | Pop) -> Self:
        if isinstance(__value, (float, int)):
            self.size += __value
        
        elif isinstance(__value, Pop) and (__value.job is None or self.job == __value.job):
            self.size += __value.size

        elif isinstance(__value, Pop):
            raise ValueError(f'Cannot add two `Pop` objects if they have different jobs.')
        
        else:
            raise TypeError(f'Cannot add type {type(__value)} to `Pop` object.')

        return self

    def __isub__(self, __value: float | int | Pop) -> Self:
        if isinstance(__value, (float, int)):
            self.size -= __value
        
        elif isinstance(__value, Pop) and (__value.job is None or self.job == __value.job):
            self.size -= __value.size

        elif isinstance(__value, Pop):
            raise ValueError(f'Cannot add two `Pop` objects if they have different jobs.')
        
        else:
            raise TypeError(f'Cannot add type {type(__value)} to `Pop` object.')

        return self

def pop_factory(size: int | float,
                job: Optional[Jobs] = None,
                stratum: Optional[Strata] = None,
                stockpile: Optional[Stockpile] = None):
    """
    ### `Pop` objects must only be created using this function!

    #### Parameters:
        - `size`: Required, must be `int` or `float`, and cannot be less than 0.
        - `job`: Optional¹ ², must be a `Jobs` member
        - `stratum`: Optional¹ ², must be a `Strata` member.
        - `stockpile`: Optinal, must be a `Stockpile` object from the `prod` module.
    
    1 - Either the `job` or the `stratum` arguments must be passed. If the two are left empty, this function will raise an error.

    2 - If both `job` and `stratum` are passed, the `job` must be a job associated with the `stratum`, 
    if it is not, this function will raise an error.
    """

    if stockpile is None:
        stockpile = Stockpile()

    if size < 0.0:
        raise ValueError(f'`Pop` object cannot have negative size.')

    if job is not None:

        if job not in Jobs:
            raise ValueError(f'The job {job} does not exist.')

        elif stratum is not None and job not in Pop.JOBS[stratum]:
            raise ValueError(f'The job {job} is not appropriate for the {stratum.name} stratum.')

        elif job in Pop.JOBS[Strata.LOWER]:
            return Pop(Strata.LOWER, size, job, stockpile)
        
        elif job in Pop.JOBS[Strata.MIDDLE]:
            return Pop(Strata.MIDDLE, size, job, stockpile)
        
        elif job in Pop.JOBS[Strata.UPPER	]:
            return Pop(Strata.UPPER, size, job, stockpile)
        
        else:
            raise ValueError(f'Although {job} exists, it is not associated with any strata.')
    
    elif stratum is None:
        raise ValueError(f'`pop_factory` requires at least one of the two arguments: `job` or `stratum`.')

    else:
        return Pop(stratum, size, stockpile=stockpile)
