from __future__ import annotations
from typing import Callable, Hashable, ItemsView, Iterator, KeysView, Self, ValuesView
from source.exceptions import NegativeAmountError
from abc import ABC, abstractmethod
from collections import UserDict
from decimal import Decimal
import copy

class Group[T: "Group"](ABC):

    """
    Abstract class for automatically adding all arithmetic overloads and preventing negative amounts. This is supposed to represent
    a physical quantity; you cannot have negative two apples.

    `_scrutinize` needs to be overwritten on all subclass after the supercall. Different subclass will need to check things particular to them.
    `_iadd` and `_isub` are inside in a template pattern to add all the adding and subtracting functionality. 
    """

    _amount_attr: str

    def __init_subclass__(cls, *, amount_attr: str) -> None:
        cls._amount_attr = amount_attr
        return super().__init_subclass__()

    @abstractmethod
    def _scrutinize(self, __value: T | Decimal, *, sub=False, mul=False, div=False) -> None:
        """ 
        Checking for multiplication and division is already implemented in the abstract class. Concrete classes must implement
        their checks for addition and subtraction and then supercall this method. 
        """

        if sub + mul + div > 1:
            raise ValueError
        
        if mul or div:
            if not isinstance(__value, Decimal):
                raise TypeError
            
            if __value < 0:
                raise NegativeAmountError
            
            if div and __value == 0:
                raise ZeroDivisionError

    def is_empty(self) -> bool:
        if getattr(self, self._amount_attr) == 0:
            return True
        
        return False

    @abstractmethod
    def _iadd(self, __value: T) -> None:
        ...

    def __iadd__(self, __value: T) -> Self:
        self._scrutinize(__value)
        self._iadd(__value)
        return self

    def __add__(self, __value: T) -> T:
        new = copy.deepcopy(self)
        new += __value
        return new  # type: ignore

    @abstractmethod
    def _isub(self, __value: T) -> None:
        ...
    
    def __isub__(self, __value: T) -> Self:
        self._scrutinize(__value, sub=True)
        self._isub(__value)
        return self

    def __sub__(self, __value: T) -> T:
        new = copy.deepcopy(self)
        new -= __value
        return new  # type: ignore

    def __imul__(self, __value: Decimal) -> Self:
        self._scrutinize(__value, mul=True)
        quantity: Decimal = getattr(self, self._amount_attr)

        product = quantity * __value
        setattr(self, self._amount_attr, product)
        return self

    def __mul__(self, __value: Decimal) -> T:
        new = copy.deepcopy(self)
        new *= __value
        return new  # type: ignore

    def __itruediv__(self, __value: Decimal) -> Self:
        self._scrutinize(__value, div=True)
        quantity: Decimal = getattr(self, self._amount_attr)

        quotient = quantity / __value
        setattr(self, self._amount_attr, quotient)
        return self

    def __truediv__(self, __value: Decimal) -> T:
        new = copy.deepcopy(self)
        new /= __value
        return new  # type: ignore

    def __repr__(self) -> str:
        return f'<{type(self).__name__}: {getattr(self, self._amount_attr)}>'

class Dyct[K: Hashable, V: Group](ABC, UserDict):

    """
    `Dyct` stands for Dynamic Dict. This `Dyct`s should behave like `default dict`s except with multiple default 
    values and operation overloading already built into them.
    """

    _factory: Callable[[K], V]

    @abstractmethod
    def _scrutinize(self, __key: K) -> None:
        """ Checks if the key is valid before allowing `getitem` or `setitem` to be called. """

    def _fix(self) -> None:
        for key, value in copy.copy(self).items():
            if value.is_empty():
                del self[key]

    def __init_subclass__(cls, *, factory: Callable[[K], V]) -> None:
        cls._factory = factory  # type: ignore
        return super().__init_subclass__()

    def __init__(self, initial_dict: dict[K, V]) -> None:
        super().__init__(initial_dict)

    def __setitem__(self, __key: K, __value) -> None:
        self._scrutinize(__key)
        super().__setitem__(__key, __value)
        self._fix()

    def __getitem__(self, __key: K) -> V:
        self._scrutinize(__key)

        try:
            return super().__getitem__(__key)
        
        except KeyError:
            return self._factory(__key)

    def __iter__(self) -> Iterator[K]:
        return super().__iter__()
    
    @abstractmethod
    def _iadd(self, __value: Dyct[K, V] | V) -> None:
        ...

    def __iadd__(self, __value: Dyct[K, V] | V) -> Self:
        self._iadd(__value)
        return self

    def __add__(self, __value: Dyct[K, V] | V) -> Dyct[K, V]:
        new = copy.deepcopy(self)
        new += __value
        return new

    @abstractmethod
    def _isub(self, __value: Dyct[K, V] | V) -> None:
        ...

    def __isub__(self, __value: Dyct[K, V] | V) -> Self:
        self._isub(__value)
        self._fix()
        return self

    def __sub__(self, __value: Dyct[K, V] | V) -> Dyct[K, V]:
        new = copy.deepcopy(self)
        new -= __value
        return new

    def __imul__(self, __value: Decimal) -> Self:
        for value in self.values():
            value *= __value
        
        self._fix()
        return self

    def __mul__(self, __value: Decimal) -> Dyct[K, V]:
        new = copy.deepcopy(self)
        new *= __value
        return new
    
    def __itruediv__(self, __value: Decimal) -> Self:
        for value in self.values():
            value /= __value

        self._fix()
        return self

    def __truediv__(self, __value: Decimal) -> Dyct[K, V]:
        new = copy.deepcopy(self)
        new /= __value
        return new

    def keys(self) -> KeysView[K]:
        return super().keys()

    def values(self) -> ValuesView[V]:
        return super().values()

    def items(self) -> ItemsView[K, V]:
        return super().items()

    def __repr__(self) -> str:
        values = map(str, self.values())
        return f'<{type(self).__name__}: {'; '.join(values)}>'
