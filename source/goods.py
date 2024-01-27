from __future__ import annotations
from _collections_abc import dict_items, dict_values, dict_keys
import copy
import math
from typing import Iterator, Optional, Self
from dataclasses import dataclass, field
from math import isclose
from enum import Enum
from source import ABS_TOL, DECIMAL_CASES

from source.exceptions import EfficiencyError, NegativeAmountError


@dataclass
class Good:
    name: str
    base_production: int | float = 1.0
    recipe: dict[Goods, float] = field(default_factory=dict)

    def __repr__(self) -> str:
        return self.name
    
    def __post_init__(self):
        if self.recipe:
            total_proportion = sum(self.recipe.values())
            if not math.isclose(total_proportion, 1):
                raise EfficiencyError(f'The shares of inputs to make the good must sum to 100%, not {total_proportion}.')

class Goods(Enum):
    """
    This enum will serve as a container of sorts. Goods can appear more than once here, because goods can have
    more than one method of production. In this way, they will be instantiated with the same name, but the name within this
    enum will be different.
    """
    
    WHEAT = Good('Wheat', 2.35)
    IRON = Good('Iron', 0.213)

    def __repr__(self) -> str:
        return self.value.name

    @property
    def base_production(self) -> int | float:
        return self.value.base_production
    
    @property
    def recipe(self) -> dict[Goods, int | float]:
        return self.value.recipe

class Stockpile(dict):
    """
    This class inherits from `dict` and has special annotations and features.

    #### Features:
        - All the keys are annotated to be members of the `Goods` `Enum`.
        - All the values are annotated to be either `int` or `float`.
        - If a key that is not a `Goods` member and a value that is not either `int` or `float`
    are passed as keys and values respectively, this class will raise an error.
        - When an item is set to zero, it is automatically removed from the stockpile.
        - When a user tries to retrieve an item that does not exist, it creates such value and sets it to 0.0. 
    This is so it can use the `+=` in any circumstances.
    """

    def __fix(self) -> None:
        for key, value in self.copy().items():
            if not isinstance(key, Goods):
                raise TypeError(f'`Stockpile` objects can only have `Goods` as keys.')
            
            if not isinstance(value, (int, float)):
                raise TypeError(f'`Stockpile` objects can only have `int` or `float` as values.')
            
            if value < 0:
                raise NegativeAmountError(f'`Stockpile` object cannot have negative values.')
            
            if isclose(value, 0, abs_tol=ABS_TOL):
                del self[key]
            
            else:
                super().__setitem__(key, round(value, DECIMAL_CASES))  # Prevents infinite recursion.

    def keys(self) -> dict_keys[Goods, int | float]:
        return super().keys()

    def values(self) -> dict_values[Goods, int | float]:
        return super().values()

    def items(self) -> dict_items[Goods, int | float]:
        return super().items()

    def __init__(self, arg: Optional[dict[Goods, int | float]] = None) -> None:
        if not arg:
            return super().__init__(dict())
        
        super().__init__(arg)
        self.__fix()

    def __setitem__(self, __key: Goods, __value: int | float) -> None:
        super().__setitem__(__key, round(__value, DECIMAL_CASES))
        self.__fix()

    def __getitem__(self, __key: Goods) -> int | float:
        try:
            if isinstance(__key, Goods):
                return super().__getitem__(__key)  # type: ignore

            else:
                raise TypeError(f'`Stockpile` objects can only have `Goods` as keys.')
        
        except KeyError:
            return 0

    def __iter__(self) -> Iterator[Goods]:
        return super().__iter__()

    def __scrutinize(self, __value: Stockpile | int | float, *, sub=False, mul=False, div=False):

        if div:
            if sub:
                raise ValueError('An arithmetic operation can\'t be both subtraction and division.')
            
            if mul:
                raise ValueError('An arithmetic operation can\'t be both multiplication and division.')
            
            if not isinstance(__value, (int, float)):
                raise TypeError(f'`Stockpile` objects can only be divided by integers or floating points.')
            
            if __value == 0:
                raise ZeroDivisionError(f'Cannot divide `Stockpile` object by zero.')
            
            if __value < 0:
                raise NegativeAmountError(f'Cannot divide `Stockpile` object by negative numbers.')
        
        elif mul:
            if sub:
                raise ValueError('An arithmetic operation can\'t be both subtraction and multiplication.')
            
            if not isinstance(__value, (int, float)):
                raise TypeError(f'`Stockpile` objects can only be multiplied by integers or floating points.')

            if __value < 0:
                raise NegativeAmountError(f'Cannot multiply `Stockpile` object by negative numbers.')

        elif not isinstance(__value, Stockpile):
                raise TypeError(f'Only other `Stockpile` objects can be added to a `Stockpile` object.')
            
        elif sub:
            for good, amount in __value.items():
                if amount > self[good]:
                    raise NegativeAmountError(f'Operation resulted in a `Stockpile` object with negative goods.')

    def __add__(self, __value: Stockpile) -> Stockpile:

        self.__scrutinize(__value)

        new = copy.deepcopy(self)

        for good, amount in __value.items():
            new[good] += amount
        
        return new

    def __sub__(self, __value: Stockpile) -> Stockpile:

        self.__scrutinize(__value, sub=True)

        new = copy.deepcopy(self)

        for good, amount in __value.items():
            new[good] -= amount
        
        new.__fix()
        return new

    def __iadd__(self, __value: Stockpile) -> Self:
        
        self.__scrutinize(__value)

        for good, amount in __value.items():
            self[good] = self[good] + amount
        
        return self
    
    def __isub__(self, __value: Stockpile) -> Self:
        
        self.__scrutinize(__value, sub=True)
        
        for good, amount in __value.items():
            self[good] = self[good] - amount  
        
        self.__fix()
        return self
    
    def __truediv__(self, __value: int | float) -> Stockpile:

        self.__scrutinize(__value, div=True)

        divided = Stockpile()

        for good, amount in self.items():
            divided[good] = amount / __value
        
        return divided
    
    def __mul__(self, __value: int | float) -> Stockpile:

        self.__scrutinize(__value, mul=True)

        if __value == 1:
            return copy.deepcopy(self)
        
        multiplied = Stockpile()
        if __value == 0:
            return multiplied

        for good, amount in self.items():
            multiplied[good] = amount * __value
        
        return multiplied

    def reset_to(self, __value: Stockpile) -> None:
        self.__scrutinize(__value)

        keys = list(self.keys())

        for key in keys:
            self[key] = __value[key]
