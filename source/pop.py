from __future__ import annotations
from decimal import Decimal, DivisionByZero, InvalidOperation, getcontext
from source.goods import Products, Stock, create_stock
from typing import TYPE_CHECKING, Optional, overload
from source.exceptions import NegativeAmountError
from dataclasses import dataclass, field
from source import num, unemployed_key
from source.abcs import Dyct, Group
from enum import Enum, auto
D = getcontext().create_decimal

if TYPE_CHECKING:
    from algs import sharing_alg

class Strata(Enum):
    LOWER = auto()
    MIDDLE = auto()
    UPPER = auto()

    @property
    def needs(self) -> dict[Products, Decimal]:

        match self:

            case Strata.LOWER:
                return {Products.FLOUR: D(1)}

            case Strata.MIDDLE:
                return {Products.FLOUR: D(1.5)}
            
            case _ :
                raise KeyError(f'`Strata` {self.name} has no needs assigned to it.')

    @property
    def jobs(self) -> tuple[Jobs, ...]:

        match self:

            case Strata.LOWER:
                return Jobs.FARMER, Jobs.MINER, Jobs.CRAFTSMAN
            
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
    UNEMPLOYED = auto()
    FARMER = auto()
    MINER = auto()
    CRAFTSMAN = auto()
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

def weighted_mean(val1: Decimal, val2: Decimal, weight1: Decimal, weight2: Decimal, /):
    total_weight = weight1 + weight2
    proportion1 = weight1 / total_weight
    proportion2 = weight2 / total_weight
    return val1 * proportion1 + val2 * proportion2

@dataclass(order=True)
class Pop(Group["Pop"], amount_attr='size'):
    """
    Do not instantiate. Use the `PopFactory` class instead.

    Subclass of the `Group` abstract class. This class represents a population.

    Its behaviour can be changed by changing the constant values here defined.
    """

    WELFARE_THRESHOLD = D('0.51')  # Pops with a welfare higher than or equal to this value will grow and promote, otherwise decline.
    GROWTH_RATE = D('0.05')  # It will grow by 5 people per 100 people.
    PROMOTE_RATE = D('0.01')  # It will promote by 1 person per 100 people.

    OLD_WELFARE_WEIGHT = D(1/3)
    NEW_WELFARE_WEIGHT = D(2/3)

    BASE_WELFARE = D(0.5)  # The welfare that newly initialized `Pop` objects should have.
    ZERO_SIZE_WELFARE = D(0)  # The welfare a `Pop` has when its size is zero.

    size: Decimal = field(compare=True)
    welfare: Decimal = field(compare=False)
    stratum: Strata = field(compare=False)
    job: Jobs = field(compare=False)

    def _scrutinize(self, __value: Pop | Decimal, *, sub=False, mul=False, div=False) -> None:
        if not isinstance(__value, (Pop, Decimal)):
            raise TypeError(f'Cannot perform math between `Pop` and `{type(__value).__name__}`.')
        
        elif isinstance(__value, Decimal):
            return super()._scrutinize(__value, sub=sub, mul=mul, div=div)
        
        elif __value.job != self.job:
            raise ValueError(f'Cannot perform arithmetic operations between pops with different jobs.')
            
        elif self.stratum != __value.stratum:
            raise ValueError(f'Cannot perform arithmetic operations between pops of different strata.\nInfo: {self.stratum}, {__value.stratum}')

        elif sub and __value.size > self.size:
            raise NegativeAmountError(f'Taking {__value.size} pops from {self.size} pops results in negative size.')

        elif sub and __value.size * __value.welfare > self.size * self.welfare:
            raise NegativeAmountError(f'Taking a welfare pool of {__value.size * __value.welfare} from {self.size * self.welfare} results in negative welfare.')

    def _iadd(self, __value: Pop) -> None:
        try:
            self.welfare = weighted_mean(self.welfare, __value.welfare, self.size, __value.size)
        
        except (InvalidOperation, DivisionByZero):
            self.welfare = self.ZERO_SIZE_WELFARE
            self.size = D(0)

        else:
            self.size = self.size + __value.size

    def _isub(self, __value: Pop) -> None:
        try:
            self.welfare = weighted_mean(self.welfare, __value.welfare, self.size, -__value.size)

        except (InvalidOperation, DivisionByZero):
            self.size = D(0)

        else:
            self.size = self.size - __value.size

        if self.size == D(0):
            self.welfare = self.ZERO_SIZE_WELFARE

    def calc_consumption(self) -> Stock:
        """ Returns a `Stock` object containing how much this pop would need to eventually reach 1.0 welfare. """

        return create_stock({product: need * self.size for product, need in self.stratum.needs.items()})

    def update_welfare(self, consumption: Stock, stockpile: Stock, /):
        """
        This method only calculates the new welfare of the object based on the passed arguments and its current welfare.
        Changes to the stockpile should be computed from outside this method.
        """

        if self.size == 0:  # This prevents (InvalidOperation, DivisionByZero)
            self.welfare = self.ZERO_SIZE_WELFARE
            return

        welfare = D(0)
        for product, need in consumption.items():
            welfare += min([D(1), stockpile[product].amount / need.amount])

        welfare /= len(self.stratum.needs)
        self.welfare = weighted_mean(self.welfare, welfare, self.OLD_WELFARE_WEIGHT, self.NEW_WELFARE_WEIGHT)

    def resize(self):
        """ Resizes the population based on its welfare. """

        if self.welfare >= self.WELFARE_THRESHOLD:
            self.size *= 1 + self.GROWTH_RATE

        else:
            self.size *= 1 - self.GROWTH_RATE
        
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
        Returns a `Pop` object of a higher stratum if promotion is possible for the object's stratum. 
        Checking wheter this method should or shouldn't be run based on the object's welfare is not 
        part of its responsability. Use the `promotes` method.
        """

        if self.stratum == Strata.LOWER:
            size = self.size * self.PROMOTE_RATE
            return PopFactory.stratum_makepop(Strata.MIDDLE, size, self.welfare)
        
        else:
            raise NotImplementedError   

class PopFactory:

    @staticmethod
    def _validate_size(size: num, /) -> Decimal:
        if not isinstance(size, (Decimal, int, float, str)):
            raise TypeError(f'{type(size).__name__} type is not allowed for `size` parameter.')
        
        if not isinstance(size, Decimal):
            size = D(size)

        if size < 0:
            raise NegativeAmountError(f'Sizes cannot be negative, but {size} was passed.')
        
        return size

    @staticmethod
    def _validate_welfare(size: num, welfare: num, /) -> Decimal:
        if not isinstance(welfare, (Decimal, int, float, str)):
            raise TypeError(f'{type(welfare).__name__} type is not allowed for `welfare` parameter.')
        
        if not isinstance(welfare, Decimal):
            welfare = D(welfare)

        if 0 > welfare or welfare > 1:
            raise ValueError(f'The `welfare` argument must be between 0 and 1, but {welfare} was passed.')
        
        if size == 0:
            return Pop.ZERO_SIZE_WELFARE

        return welfare

    @classmethod
    def job_makepop(cls, job: Jobs, size: num = D(0), welfare: num = D(Pop.BASE_WELFARE), /) -> Pop:
        if not isinstance(job, Jobs):
            raise TypeError(f'{type(job).__name__} type is not allowed for the `job` parameter.')
        
        if job == Jobs.UNEMPLOYED:
            raise ValueError(f'The `job` parameter cannot be {Jobs.UNEMPLOYED.name}.')
        
        size = cls._validate_size(size)
        welfare = cls._validate_welfare(size, welfare)

        return Pop(size, welfare, job.stratum, job)

    @classmethod
    def stratum_makepop(cls, stratum: Strata, size: num = D(0), welfare: num = D(Pop.BASE_WELFARE), /) -> Pop:
        if not isinstance(stratum, Strata):
            raise TypeError
        
        size = cls._validate_size(size)
        welfare = cls._validate_welfare(size, welfare)

        return Pop(size, welfare, stratum, Jobs.UNEMPLOYED)

    @classmethod
    def empty(cls, key) -> Pop:        
        return cls.stratum_makepop(key[0]) if isinstance(key, tuple) else cls.job_makepop(key)

    def __init__(self, key: Jobs | Strata) -> None:
        if not isinstance(key, (Jobs, Strata)):
            raise TypeError
        
        self.key = key

    def __call__(self, size: num = D(0), welfare: num = Pop.BASE_WELFARE, /) -> Pop:
        size = self._validate_size(size)
        welfare = self._validate_welfare(size, welfare)

        if isinstance(self.key, Strata):
            return self.stratum_makepop(self.key, size, welfare)
        
        else:
            return self.job_makepop(self.key, size, welfare)

class Commune(Dyct[Jobs | unemployed_key, Pop], factory=PopFactory.empty):
    def _scrutinize(self, __key: Jobs | unemployed_key) -> None:
        if not isinstance(__key, (Jobs, tuple)):
            raise TypeError(f'{type(__key).__name__} type was used as a key for a commune.')
        
        if __key == Jobs.UNEMPLOYED:
            raise ValueError(f'{Jobs.UNEMPLOYED.name} was passed as a key to a commune.')
        
        if isinstance(__key, Jobs):
            return
        
        if len(__key) != 2:
            raise ValueError(f'A tuple of length {len(__key)} was passed as a key to a commune.')
        
        if not isinstance(__key[0], Strata) or __key[1] != Jobs.UNEMPLOYED:
            raise ValueError(f'The tuple {__key} was passed to a commune.')

    @overload
    def __getitem__(self, __key: Jobs | unemployed_key) -> Pop:
        ...
    
    @overload
    def __getitem__(self, __key: Strata) -> Commune:
        ...

    def __getitem__(self, __key: Jobs | unemployed_key | Strata) -> Commune | Pop:
        if isinstance(__key, Strata):
            return Commune({key: pop for key, pop in self.items() if pop.stratum == __key})

        return super().__getitem__(__key)

    def _iadd(self, __value: Commune | Pop) -> None:
        if isinstance(__value, Pop):
            try:
                self[__value.job] += __value
            
            except ValueError:
                self[__value.stratum, Jobs.UNEMPLOYED] += __value
        
        elif isinstance(__value, Commune):
            for key, value in __value.items():
                self[key] += value
        
        else:
            raise TypeError
    
    def _isub(self, __value: Commune | Pop) -> None:
        if isinstance(__value, Pop):
            try:
                self[__value.job] -= __value
            
            except ValueError:
                self[__value.stratum, Jobs.UNEMPLOYED] -= __value
        
        elif isinstance(__value, Commune):
            for key, value in __value.items():
                self[key] -= value
        
        else:
            raise TypeError

    @property
    def size(self) -> Decimal:
        return D( sum(pop.size for pop in self.values()) )

    def get_share_of(self, __key: Jobs | unemployed_key | Strata, /) -> Decimal:
        """ 
        Calculates the share of the population corresponding to the passed __key argument in relation to 
        the total size of the community.

        If a `Strata` is passed, then it will calculate the size of all the pops 
        of that stratum in relation to the total size of the community.
        """
    
        try:
            return self[__key].size / self.size
        
        except (InvalidOperation, DivisionByZero):
            return D(0)

    def calc_goods_demand(self) -> Stock:
        total_demand = create_stock()
        
        for pop in self.values():
            total_demand += pop.calc_consumption()

        return total_demand

    def update_welfares(self, stockpile: Stock, algorithm: sharing_alg, /):
        """ The sharing algorithms are interchageable through the strategy pattern. """
        
        algorithm(self, stockpile)

    def resize_all(self):
        for pop in self.values():
            pop.resize()

    def promote_all(self) -> Commune:
        promoted = CommuneFactory.create_by_job()

        for pop in self.values():
            if pop.can_promote(): 
                promoted += pop.promote()
        
        return promoted

    def unemploy_all(self) -> None:
        """ Resets all pop's jobs to UNEMPLOYED. """

        for key in self.copy().keys():
            pop = self.pop(key)
            pop.job = Jobs.UNEMPLOYED
            self += pop

class CommuneFactory:

    @staticmethod
    def _fmt_init_dict(want: dict[Jobs | Strata, num | tuple[num, num]] | None, *,
                       stratum=False,
                       welfare=False) -> dict[Jobs | unemployed_key, Pop]:
        
        if want is None: return {}
        if not isinstance(want, dict): raise TypeError

        want_ = {}
        for key, val in want.items():
            if stratum:
                key_ = key, Jobs.UNEMPLOYED
                want_[key_] = PopFactory.stratum_makepop(key, *val) if welfare else PopFactory.stratum_makepop(key, val)  # type: ignore
            
            else:
                want_[key] = PopFactory.job_makepop(key, *val) if welfare else PopFactory.job_makepop(key, val)  # type: ignore
        
        return want_

    @classmethod
    def create_by_job(cls, want: Optional[dict[Jobs, num]] = None, /) -> Commune:
        init_dict = cls._fmt_init_dict(want)  # type: ignore
        return Commune(init_dict)
    
    @classmethod
    def create_by_stratum(cls, want: Optional[dict[Strata, num]] = None, /) -> Commune:
        init_dict = cls._fmt_init_dict(want, stratum=True)  # type: ignore
        return Commune(init_dict)
    
    @classmethod
    def create_by_job_w_w(cls, want: Optional[dict[Jobs, tuple[num, num]]] = None, /) -> Commune:
        init_dict = cls._fmt_init_dict(want, welfare=True)  # type: ignore
        return Commune(init_dict)
    
    @classmethod
    def create_by_stratum_w_w(cls, want: Optional[dict[Strata, tuple[num, num]]] = None, /) -> Commune:
        init_dict = cls._fmt_init_dict(want, stratum=True, welfare=True)  # type: ignore
        return Commune(init_dict)

    def __init__(self, *keys: Jobs | Strata, welfare: num = D(Pop.BASE_WELFARE)) -> None:
        self.welfare = D(welfare)
        self.keys = keys

        if self.welfare < 0 or self.welfare > 1:
            raise ValueError
    
        if any(not isinstance(key, (Jobs, Strata)) for key in self.keys): raise TypeError

    def __call__(self, *sizes: num) -> Commune:
        if len(sizes) != len(self.keys): raise IndexError
        init_dict: dict[Jobs | unemployed_key, Pop] = {}

        for key, size in zip(self.keys, sizes):
            if isinstance(key, Jobs):
                init_dict[key] = PopFactory.job_makepop(key, size, self.welfare)
            
            else:
                init_dict[key, Jobs.UNEMPLOYED] = PopFactory.stratum_makepop(key, size, self.welfare)
        
        return Commune(init_dict)
