from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Self
from enum import Enum, auto
from math import isclose
from source.goods import Goods, Stockpile

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
        - `_size`: The amount of people in this specific population - can be a `float` or an `int`.
        - `job`: One of the jobs in the `Jobs` `Enum`. Stratas have jobs specific to them and cannot have jobs from another stratum.
    
    #### Additional attributes:
        - `promotes`: The stratum from the `Strata` `Enum` that this object's stratum promotes to; or `None` if does not promote.
    e.g.: `Strata.LOWER` promotes to `Strata.MIDDLE`.
        - `stockpile`: a pointer to a `Stockpile` object within the parent object that this `Pop` object is composite of.

    #### Properties:
        - `consumption`: A `dict[Goods, float | int]` mapping the goods this `Pop` object needs and their respective needed amounts.
    `Goods` is a `Enum` member from the `Goods` `Enum` in the `goods` module. Each stratum has different needs and respective amounts.
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
    _size: int | float
    job: Optional[Jobs] = None

    @property
    def size(self) -> int | float:
        """
        This property has the purpose of preventing the size of the population from never reaching zero.
        """

        if self._size < 0.001:
            self._size = 0
        
        return self._size

    @property
    def consumption(self) -> dict[Goods, int | float]:
        return {good: need * self._size for good, need in Pop.NEEDS[self.stratum].items()}

    @property
    def welfare(self) -> float:

        if isclose(self._size, 0.0):  # This prevents ZeroDivisionError
            return 0.0

        welfare = 0.0

        for good, amount in self.consumption.items():
            try:
                welfare += min([1, self.stockpile[good] / amount])
            
            except KeyError:
                continue

        welfare /= len(Pop.NEEDS[self.stratum])
        return welfare

    def consume(self) -> Optional[Pop]:  # type: ignore
        """
        Grows or shrinks the _size of the `object` 
        and optionally returns another `Pop` object if the object's `promotes` attribute is not `None`
        """

        welfare = self.welfare
        original_size = self._size

        for good, amount in self.consumption.items():
            self.stockpile[good] -= min([Pop.NEEDS[self.stratum][good] * self._size, amount, self.stockpile[good]])

        if welfare >= Pop.WELFARE_THRESHOLD:
            self += self._size * Pop.GROWTH_RATE

            if self.promotes:
                return pop_factory(original_size * Pop.PROMOTE_RATE, self.stockpile, stratum = self.promotes)
            
        else:
            self -= self._size * Pop.GROWTH_RATE

    def link_stockpile(self, stockpile: Stockpile):
        self.stockpile = stockpile

    def __post_init__(self) -> None:
        self.promotes: Optional[Strata]

        match self.stratum:
            case Strata.LOWER:
                self.promotes = Strata.MIDDLE
            
            case _:
                self.promotes = None

    def __repr__(self) -> str:
        if self.job is None:
            return f'<{self.stratum.name, self._size}>'
        
        else:
            return f'<{self.job.name}: {self._size}>'

    def __iadd__(self, __value: float | int | Pop) -> Self:
        if isinstance(__value, (float, int)):
            self._size += __value
        
        elif isinstance(__value, Pop) and (__value.job is None or self.job == __value.job):
            self._size += __value._size

        elif isinstance(__value, Pop):
            raise ValueError(f'Cannot add two `Pop` objects if they have different jobs.')
        
        else:
            raise TypeError(f'Cannot add type {type(__value)} to `Pop` object.')

        return self

    def __isub__(self, __value: float | int | Pop) -> Self:
        if isinstance(__value, (float, int)):
            self._size -= __value
        
        elif isinstance(__value, Pop) and (__value.job is None or self.job == __value.job):
            self._size -= __value._size

        elif isinstance(__value, Pop):
            raise ValueError(f'Cannot add two `Pop` objects if they have different jobs.')
        
        else:
            raise TypeError(f'Cannot add type {type(__value)} to `Pop` object.')

        return self

def pop_factory(_size: int | float, stockpile: Stockpile, job: Optional[Jobs] = None, stratum: Optional[Strata] = None) -> Pop:
    """
    ### `Pop` objects must only be created using this function!

    #### Parameters:
        - `_size`: Required, must be `int` or `float`, and cannot be less than 0.
        - `stockpile`: Required, this is expected to be the `Stockpile` object from the parent class
    which this generated `Pop` object will be composite of. 
        - `job`: Optional¹ ², must be a `Jobs` member
        - `stratum`: Optional¹ ², must be a `Strata` member.
    
    1 - Either the `job` or the `stratum` arguments must be passed. If the two are left empty, this function will raise an error.

    2 - If both `job` and `stratum` are passed, the `job` must be a job associated with the `stratum`, 
    if it is not, this function will raise an error.
    """

    if _size < 0.0:
        raise ValueError(f'`Pop` object cannot have negative _size.')

    if not isinstance(stockpile, Stockpile):
        raise TypeError('`stockpile` argument must be a `Stockpile` object.')

    if job is not None:

        if job not in Jobs:
            raise ValueError(f'The job {job} does not exist.')

        elif stratum is not None and job not in Pop.JOBS[stratum]:
            raise ValueError(f'The job {job} is not appropriate for the {stratum.name} stratum.')

        elif job in Pop.JOBS[Strata.LOWER]:
            pop = Pop(Strata.LOWER, _size, job)
            pop.link_stockpile(stockpile)
            return pop
        
        elif job in Pop.JOBS[Strata.MIDDLE]:
            pop = Pop(Strata.MIDDLE, _size, job)
            pop.link_stockpile(stockpile)
            return pop
        
        elif job in Pop.JOBS[Strata.UPPER]:
            pop = Pop(Strata.UPPER, _size, job)
            pop.link_stockpile(stockpile)
            return pop
        
        else:
            raise ValueError(f'Although {job} exists, it is not associated with any strata.')
    
    elif stratum is None:
        raise ValueError(f'`pop_factory` requires at least one of the two arguments: `job` or `stratum`.')

    else:
        pop = Pop(stratum, _size)
        pop.link_stockpile(stockpile)
        return pop
