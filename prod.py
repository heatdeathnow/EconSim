from __future__ import annotations
from _collections_abc import dict_items, dict_values
from typing import Iterator, Optional, Sequence
from dataclasses import dataclass
from math import isclose
from enum import Enum


@dataclass
class Good:
    name: str
    recipe: Optional[Sequence[Recipe]] = None

class Recipe:
    """To be implemented"""

class Goods(Enum):
    WHEAT = Good('Wheat')
    IRON = Good('Iron')

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

    def fix(self) -> None:
        for key, value in self.copy().items():
            if not isinstance(key, Goods):
                raise TypeError(f'`Stockpile` objects can only have `Goods` as keys.')
            
            if not isinstance(value, (int, float)):
                raise TypeError(f'`Stockpile` objects can only have `int` or `float` as values.')
            
            if value < 0.0:
                raise ValueError(f'`Stockpile` object cannot have negative values.')
            
            if isclose(value, 0.0):
                del self[key]

    def values(self) -> dict_values[Goods, int | float]:
        return super().values()

    def items(self) -> dict_items[Goods, int | float]:
        return super().items()

    def __init__(self, arg: Optional[dict[Goods, int | float]] = None) -> None:
        if not arg:
            return super().__init__(dict())
        
        super().__init__(arg)
        self.fix()

    def __setitem__(self, __key: Goods, __value: int | float) -> None:
        super().__setitem__(__key, __value)
        self.fix()

    def __getitem__(self, __key: Goods) -> int | float:
        try:
            if isinstance(__key, Goods):
                return super().__getitem__(__key)

            else:
                raise TypeError(f'`Stockpile` objects can only have `Goods` as keys.')
        
        except KeyError:
            # self[__key] = 0.0
            return 0.0

    def __iter__(self) -> Iterator[Goods]:
        return super().__iter__()
