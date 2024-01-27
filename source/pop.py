from __future__ import annotations
from _collections_abc import dict_items, dict_values, dict_keys
from collections.abc import Iterator
from typing import Callable, Literal, Mapping, Optional, Self, Sequence, overload
from source.exceptions import NegativeAmountError
from source.goods import Goods, Stockpile
from dataclasses import dataclass
from enum import Enum, auto
import math
import numpy as np
import copy
from source import ABS_TOL, DECIMAL_CASES


class Strata(Enum):
    LOWER = auto()
    MIDDLE = auto()
    UPPER = auto()

    @property
    def needs(self) -> dict[Goods, float]:

        match self:

            case Strata.LOWER:
                return {Goods.WHEAT: 1.0}

            case Strata.MIDDLE:
                return {Goods.WHEAT: 1.5, Goods.IRON: 1.0}
            
            case _ :
                raise KeyError(f'`Strata` {self.name} has no needs assigned to it.')

    @property
    def jobs(self) -> tuple[Jobs, ...]:

        match self:

            case Strata.LOWER:
                return Jobs.FARMER, Jobs.MINER
            
            case Strata.MIDDLE:
                return Jobs.SPECIALIST,
            
            case _ :
                raise KeyError(f'`Strata` has no jobs assigned to it.')

    @property
    def promotes(self) -> Optional[Strata]:
        match self:

            case Strata.LOWER:
                return Strata.MIDDLE
            
            case Strata.MIDDLE:
                return None
            
            case _ :
                raise KeyError(f'stratum `{self}` has no promotion assigned to it.')

class Jobs(Enum):
    NONE = auto()
    FARMER = auto()
    MINER = auto()
    SPECIALIST = auto()

    @property
    def stratum(self) -> Strata:
        
        if self in Strata.LOWER.jobs:
            return Strata.LOWER
        
        elif self in Strata.MIDDLE.jobs:
            return Strata.MIDDLE
        
        elif self in Strata.UPPER.jobs:
            return Strata.UPPER

        else:
            raise KeyError(f'Job {self.name} is not assigned to any stratum.')
    
    def __repr__(self) -> str:
        return self.name

@dataclass
class Pop:

    # ===== CONFIGURATIONS =====

    WELFARE_THRESHOLD = 0.51  # Pops with a welfare higher than or equal to this value will grow and promote, otherwise decline.
    GROWTH_RATE = 0.05  # It will grow by 5 people per 100 people.
    PROMOTE_RATE = 0.01  # It will promote by 1 person per 100 people.

    OLD_WELFARE_WEIGHT = 1/3
    NEW_WELFARE_WEIGHT = 2/3

    BASE_WELFARE = 0.5  # The welfare that newly initialized `Pop` objects should have.
    ZERO_SIZE_WELFARE = 0.0  # The welfare a `Pop` has when its size is zero.

    # ==========================

    size: int | float
    welfare: int | float
    stratum: Strata
    job: Jobs

    def __scrutinize(self, __value: Pop, sub: bool = False):
        """ 
        This method checks if it is possible to carry out arithmetic calculations with the passed object.
        If not, it raises an exception.
        """

        if not isinstance(__value, Pop):
            raise TypeError(f'Arithmetic operations between a `Pop` type and a `{type(__value)}` type are not allowed.')

        if self.job != __value.job and self.job != Jobs.NONE and __value.job != Jobs.NONE:
            raise ValueError(f'Cannot perform arithmetic operations between pops with different jobs.\nInfo: {self.job}, {__value.job}')
        
        if self.stratum != __value.stratum:
            raise ValueError(f'Cannot perform arithmetic operations between pops of different strata.\nInfo: {self.stratum}, {__value.stratum}')

        if sub and __value.size > self.size:
            raise NegativeAmountError(f'Taking {__value.size} pops from {self.size} pops results in negative size.')

        if sub and __value.size * __value.welfare > self.size * self.welfare:
            raise NegativeAmountError(f'Taking a welfare pool of {__value.size * __value.welfare} from {self.size * self.welfare} results in negative welfare.')

    def __add__(self, __value: Pop) -> Pop:
        self.__scrutinize(__value)

        try:
            size = round(self.size + __value.size, DECIMAL_CASES)
            welfare = round(float(np.average([self.welfare, __value.welfare], weights=[self.size, __value.size])), DECIMAL_CASES)
            return PopFactory.job(self.job, size, welfare)

        except ZeroDivisionError:
            return PopFactory.job(self.job)

    def __sub__(self, __value: Pop) -> Pop:
        self.__scrutinize(__value, True)

        try:
            size = round(self.size - __value.size, DECIMAL_CASES)
            welfare = round(float(np.average([self.welfare, __value.welfare], weights=[self.size, -__value.size])), DECIMAL_CASES)
            return PopFactory.job(self.job, size, welfare)

        except ZeroDivisionError:
            return PopFactory.job(self.job)

    def __iadd__(self, __value: Pop) -> Self:
        self.__scrutinize(__value)

        try:
            self.welfare = round(float(np.average([self.welfare, __value.welfare], weights=[self.size, __value.size])), DECIMAL_CASES)
            self.size = round(self.size + __value.size, DECIMAL_CASES)
        
        except ZeroDivisionError:
            self.welfare = Pop.ZERO_SIZE_WELFARE
            self.size = 0

        finally:
            return self

    def __isub__(self, __value: Pop) -> Self:
        self.__scrutinize(__value, True)

        try:
            self.welfare = round(float(np.average([self.welfare, __value.welfare], weights=[self.size, -__value.size])), DECIMAL_CASES)
            self.size = round(self.size - __value.size, DECIMAL_CASES)

        except ZeroDivisionError:
            self.welfare = Pop.ZERO_SIZE_WELFARE
            self.size = 0

        finally:
            return self

    def __eq__(self, __value: Pop) -> bool:
        return self.size == __value.size

    def __gt__(self, __value: Pop) -> bool:
        return self.size > __value.size

    def __ge__(self, __value: Pop) -> bool:
        return self.size >= __value.size

    def __lt__(self, __value: Pop) -> bool:
        return self.size < __value.size

    def __le__(self, __value: Pop) -> bool:
        return self.size <= __value.size

    def __repr__(self) -> str:
        """The stratum is implicit in each job except for NONE."""

        if self.job == Jobs.NONE:
            return f'<{self.stratum.name}: {self.size}>'
        
        else:
            return f'<{self.job.name}: {self.size}>'

    def calc_consumption(self) -> Stockpile:
        return Stockpile({good: round(need * self.size, DECIMAL_CASES) for good, need in self.stratum.needs.items()})

    def update_welfare(self, consumption: Stockpile, stockpile: Stockpile):
        """
        This method only calculates the new welfare of the object based on the passed arguments and its current welfare.
        Changes to the stockpile should be computed from outside this method.
        """

        if math.isclose(self.size, 0.0, abs_tol=ABS_TOL):  # This prevents ZeroDivisionError
            self.welfare = Pop.ZERO_SIZE_WELFARE
            return

        welfare = 0.0
        for good, amount in consumption.items():
            welfare += min([1, stockpile[good] / amount])

        welfare /= len(self.stratum.needs)
        self.welfare = float(np.average([self.welfare, welfare], weights=[Pop.OLD_WELFARE_WEIGHT, Pop.NEW_WELFARE_WEIGHT]))

        if math.isclose(self.welfare, 0, abs_tol=ABS_TOL):
            self.welfare = 0
        
        else:
            self.welfare = round(self.welfare, DECIMAL_CASES)

    def resize(self):
        """ Resizes the population based on its welfare. """

        if self.welfare >= Pop.WELFARE_THRESHOLD:
            self.size += self.size * Pop.GROWTH_RATE

        else:
            self.size -= self.size * Pop.GROWTH_RATE
        
        if math.isclose(self.size, 0, abs_tol=ABS_TOL):
            self.size = 0
        
        else:
            self.size = round(self.size, DECIMAL_CASES)
    
    def can_promote(self) -> bool:
        """ Checks if the object can promote to a higher stratum based on its stratum and welfare. """

        if self.stratum in (Strata.MIDDLE, Strata.UPPER):
            return False
        
        elif self.welfare < Pop.WELFARE_THRESHOLD:
            return False
        
        else:
            return True

    def promote(self) -> Pop:
        """
        Returns a `Pop` object of a higher stratum if promotion is possible for the objects stratum. 
        Checking wheter this method should or shouldn't be run based on the object's welfare is not 
        part of its responsability. Use the `promotes` method.
        """

        match self.stratum:
            case Strata.LOWER:
                size = round(self.size * Pop.PROMOTE_RATE, DECIMAL_CASES)
                return PopFactory.stratum(Strata.MIDDLE, size, self.welfare)
            
            case _ :
                raise NotImplementedError            

class PopFactory:

    """ Container class for `Pop` factory methods. """

    @staticmethod
    def __validate_size(size: int | float):
        if not isinstance(size, (int, float)):
            raise TypeError(f'The size parameter only accepts `int` or `float` types, but a `{type(size)}` type was passed.')
        
        if size < 0.0:
            raise ValueError(f'The `size` parameter only accepts positive values, but {size} was passed.')
    
    @staticmethod
    def __validate_welfare(welfare: int | float):
        if not isinstance(welfare, (int, float)):
            raise TypeError(f'The welfare parameter only accepts `float` types, but a `{type(welfare)}` type was passed.')

        if not (0.0 <= welfare <= 1.0):
            raise ValueError(f'The `welfare` parameter only accepts values between 0 and 1, but {welfare} was passed.')

    @classmethod
    def job(cls, job: Jobs, size: int | float = 0, welfare: float = Pop.BASE_WELFARE) -> Pop:

        # job validation
        if job not in Jobs:
            raise TypeError(f'The `job` parameter only accepts members of the `Jobs` enum, but {job} was passed.')

        if job == Jobs.NONE:
            raise ValueError(f'Cannot use the `job` factory with `NONE` as a job. Use the stratum factory instead.')

        # Size and welfare validation
        cls.__validate_size(size)
        size = round(size, DECIMAL_CASES)

        if math.isclose(size, 0, abs_tol=ABS_TOL):
            welfare = Pop.ZERO_SIZE_WELFARE
        
        else:
            cls.__validate_welfare(welfare)
            welfare = round(welfare, DECIMAL_CASES)
        
        if size != 0 and size < ABS_TOL:
            size = ABS_TOL
        
        # Determining stratum.
        if job in Strata.LOWER.jobs:
            stratum = Strata.LOWER
        
        elif job in Strata.MIDDLE.jobs:
            stratum = Strata.MIDDLE
        
        elif job in Strata.UPPER.jobs:
            stratum = Strata.UPPER
        
        else:
            raise KeyError(f'Although {job} exists, it has not been assigned to any of the strata')
        
        return Pop(size, welfare, stratum, job)

    @classmethod
    def stratum(cls, stratum: Strata, size: int | float = 0, welfare: float = Pop.BASE_WELFARE) -> Pop:
        
        if stratum not in Strata:
            raise TypeError(f'`stratum` parameter only accepts members of the `Strata` enum, but {stratum} was passed.')
        
        cls.__validate_size(size)
        size = round(size, DECIMAL_CASES)

        if math.isclose(size, 0, abs_tol=ABS_TOL):
            welfare = Pop.ZERO_SIZE_WELFARE
            welfare = round(welfare, DECIMAL_CASES)
        
        else:
            PopFactory.__validate_welfare(welfare)
        
        if size != 0 and size < ABS_TOL:
            size = ABS_TOL

        return Pop(size, welfare, stratum, Jobs.NONE)

class Community(dict):

    """
    This class is intended as a container for `Pop` objects.

    `Community[Jobs]` returns a `Pop` object with the specified job. If it doesn't have one, it will create one with size 0.

    `Community[Jobs.NONE]` won't work, so `Community[Strata, Jobs.NONE]` should be used instead for retrieving unemployed 
    pops of a specific stratum.

    `Community[Strata]` will return a `Community` containing only the pops of the specified strata.

    Use `Community[Jobs] += Pop` or `Community += Pop` to add a pop to the community.

    Use `Community += Community to add all pops of the former to the prior.
    """

    def __fix(self):
        copy: dict[Jobs | tuple[Strata, Literal[Jobs.NONE]], Pop] = self.copy()

        for key, val in copy.items():
            if not isinstance(key, tuple) and key not in Jobs:
                raise TypeError(f'`Community` objects cannot take a `{type(key)}` type as a key.')
            
            if isinstance(key, tuple):
                if len(key) != 2:
                    raise ValueError('Only tuples of length 2 and type `tuple[Strata, Jobs.NONE]` are accepted as keys.')
                
                if key[0] not in Strata or key[1] != Jobs.NONE:
                    raise TypeError(f'`Community` objects only accept `tuple[Strata, Jobs.NONE]` as a tuple-key.')

            if not isinstance(val, Pop):
                raise TypeError(f'`Community` objects can only have `Pop` objets as values.')
            
            if val.size < 0 or math.isclose(val.size, 0, abs_tol=ABS_TOL):
                del self[key]

    def items(self) -> dict_items[Jobs | tuple[Strata, Literal[Jobs.NONE]], Pop]:
        return super().items()

    def values(self) -> dict_values[Jobs | tuple[Strata, Literal[Jobs.NONE]], Pop]:
        return super().values()

    def keys(self) -> dict_keys[Jobs | tuple[Strata, Literal[Jobs.NONE]], Pop]:
        return super().keys()

    def __init__(self, pops: Optional[Sequence[Pop]] = None):
        super().__init__()

        if pops is None:
            return 

        for pop in pops:            
            if pop.job != Jobs.NONE:
                self[pop.job] = pop
            
            else:
                self[pop.stratum, Jobs.NONE] = pop
        
        self.__fix()

    def __setitem__(self, __key: Jobs | tuple[Strata, Literal[Jobs.NONE]], __value: Pop):
        super().__setitem__(__key, __value)
        self.__fix()

    @overload
    def __getitem__(self, __key: Jobs | tuple[Strata, Literal[Jobs.NONE]]) -> Pop:
        """ Returns the stored `Pop` with the specified job. If this community has no such pop, it returns one with size 0. """
    
    @overload
    def __getitem__(self, __key: Strata) -> Community:
        """ Returns a community whose stored pops are only of the specified stratum. """

    def __getitem__(self, __key: Jobs | tuple[Strata, Literal[Jobs.NONE]] | Strata) -> Pop | Community:

        if __key not in Jobs and __key not in Strata and not isinstance(__key, tuple):
            raise TypeError('Can only consult `Community` pops via `Jobs`, `Strata`, or `tuple[Strata, Jobs.NONE]` as keys.')

        if isinstance(__key, tuple):
            if len(__key) != 2:
                raise ValueError('Only tuples of length 2 and type `tuple[Strata, Jobs.NONE]` are accepted as keys.')
            
            if __key[0] not in Strata or __key[1] != Jobs.NONE:
                raise TypeError(f'`Community` objects only accept `tuple[Strata, Jobs.NONE]` as a tuple-key.')
                    
        elif isinstance(__key, Strata):
            return self.__filter(__key)
        
        try:
            return super().__getitem__(__key)

        except KeyError:
            if isinstance(__key, tuple):
                return PopFactory.stratum(__key[0])

            else:
                return PopFactory.job(__key)

    def __filter(self, filter: Strata) -> Community:
        pops: list[Pop] = []

        for pop in self.values():
            if pop.stratum == filter:
                pops.append(pop)
        
        return Community(pops)
    
    def __iter__(self) -> Iterator[Jobs | tuple[Strata, Literal[Jobs.NONE]]]:
        return super().__iter__()
    
    def __scrutinize(self, __value: Pop | Community, sub: bool = False):
        """ Checks if it is possible to perform an arithmetic operation with the passed value. """

        if not isinstance(__value, (Pop, Community)):
            raise TypeError(f'`Community` object only performs arithmetic operations with `Community` or `Pop` objects, but {type(__value)} was passed.')
                
        # All further checks for size and welfare are redundant since they'll be performed inside the `Pop` class anyways.

    def __add__(self, __value: Pop | Community) -> Community:

        self.__scrutinize(__value)
        new = copy.deepcopy(self)

        if isinstance(__value, Pop) and __value.job != Jobs.NONE:
            new[__value.job] += __value
        
        elif isinstance(__value, Pop):
            new[__value.stratum, Jobs.NONE] += __value
        
        else:
            for key, pop in __value.items():  # If it is in a `Community` object, then it is already consistent and correct.
                new[key] += pop
            
        return new

    def __sub__(self, __value: Pop | Community) -> Community:

        self.__scrutinize(__value, True)
        new = copy.deepcopy(self)

        if isinstance(__value, Pop) and __value.job != Jobs.NONE:
            new[__value.job] -= __value
        
        elif isinstance(__value, Pop):
            new[__value.stratum, Jobs.NONE] -= __value
        
        else:
            for key, pop in __value.items():
                new[key] -= pop
            
        return new

    def __iadd__(self, __value: Pop | Community) -> Self:

        self.__scrutinize(__value)

        if isinstance(__value, Pop) and __value.job != Jobs.NONE:
            self[__value.job] += __value
        
        elif isinstance(__value, Pop):
            self[__value.stratum, Jobs.NONE] += __value
        
        else:
            for key, pop in __value.items():
                self[key] += pop
        
        return self

    def __isub__(self, __value: Pop | Community) -> Self:

        self.__scrutinize(__value, True)

        if isinstance(__value, Pop) and __value.job != Jobs.NONE:
            self[__value.job] -= __value
        
        elif isinstance(__value, Pop):
            self[__value.stratum, Jobs.NONE] -= __value
        
        else:
            for key, pop in __value.items():
                self[key] -= pop
        
        return self

    def __repr__(self) -> str:
        pops = self.values()
        pops = list(map(str, pops))
        return f'<Community obj.: {', '.join(pops)} >'

    @property
    def size(self) -> int | float:
        return sum(round(pop.size, DECIMAL_CASES) for pop in self.values())

    def get_share_of(self, __key: Jobs | tuple[Strata, Literal[Jobs.NONE]] | Strata) -> float:
        """ 
        Calculates the share of the population corresponding to the passed __key argument in relation to 
        the total size of the community.

        If a `Strata` is passed, then it will calculate the size of all the pops 
        of that stratum in relation to the total size of the community.
        """
    
        try:
            return self[__key].size / self.size
        
        except ZeroDivisionError:
            return 0

    def calc_goods_demand(self) -> Stockpile:

        total_demand = Stockpile()
        
        for pop in self.values():
            total_demand += pop.calc_consumption()
        
        return total_demand

    def update_welfares(self, stockpile: Stockpile, algorithm: type[SharingAlg]):
        """ The sharing algorithms are interchageable through the strategy pattern. """
        
        algorithm.share(self, stockpile)

    def resize_all(self):
        
        for pop in self.values():
            pop.resize()

    def promote_all(self) -> Community:

        promoted = Community()

        for pop in self.values():

            if pop.can_promote(): 
                promoted += pop.promote()
        
        return promoted

    def unemploy_all(self) -> None:
        """ Resets all pop's jobs to NONE. """

        keys = tuple(self.keys())

        for key in keys:
            pop = self.pop(key)
            pop.job = Jobs.NONE
            self += pop

class ComFactory:

    """ Container class for `Community` factory methods. """

    @staticmethod
    def __validate_dict(want: dict):
        if not isinstance(want, dict):
            raise TypeError(f'`ComFactory`\'s methods method only take in dictionaries, but `{type(want)}` was passed.')
    
    type __size_and_welfare = int | float | tuple[int | float, int | float]
    @classmethod
    def __create_community(cls, method: Callable, want: Optional[dict[Jobs, __size_and_welfare] | dict[Strata, __size_and_welfare]] = None):
        """ This method is cancerous. TODO: something about this. """

        if want is None:
            return Community()

        cls.__validate_dict(want)

        pops = []

        for job_stratum, size_welfare in want.items():
            try:
                if isinstance(size_welfare, tuple):
                    pops.append(method(job_stratum, *size_welfare))
                
                else:
                    pops.append(method(job_stratum, size_welfare))
        
            except (TypeError, ValueError, KeyError) as e:
                e.add_note(f"""
This occured when attemping to instantiate a pop with using the `{method.__name__}` method of the `PopFactory` class.
Info: job/stratum: {job_stratum}, size/welfare: {size_welfare}.""")
                raise e
            
        return Community(pops)

    @classmethod
    def job(cls, want: Optional[dict[Jobs, int | float]] = None) -> Community:
        """ Creates all the `Pop`s with the specified jobs and sizes and returns a `Community` containing them. """
        
        return cls.__create_community(PopFactory.job, want)  # type: ignore

    @classmethod
    def job_welfare(cls, want: Optional[dict[Jobs, tuple[int | float, int | float]]] = None) -> Community:
        """ Creates all the `Pop`s with the specified jobs, sizes and welfares and returns a `Community` containing them. """

        return cls.__create_community(PopFactory.job, want)  # type: ignore

    @classmethod
    def stratum(cls, want: Optional[dict[Strata, int | float]] = None) -> Community:
        """ Creates all the `Pop`s with the specified stratum and sizes and returns a `Community` containing them. """

        return cls.__create_community(PopFactory.stratum, want)  # type: ignore
            
    @classmethod
    def stratum_welfare(cls, want: Optional[dict[Strata, tuple[int | float, int | float]]] = None) -> Community:
        """ Creates all the `Pop`s with the specified stratum, sizes and welfare and returns a `Community` containing them. """

        return cls.__create_community(PopFactory.stratum, want)  # type: ignore



from source.utils import SharingAlg
