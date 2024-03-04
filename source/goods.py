from __future__ import annotations
from source.exceptions import NegativeAmountError
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from typing import Callable, Optional
from source.abcs import Group, Dyct
from functools import partial
from enum import Enum, auto
from math import isclose
from source import num
D = getcontext().create_decimal

class Technology:
    """
    Represents means of production. How much of a good is made, if it takes other goods and inputs.
    """
    
    def __init__(self, base_yield: Decimal, recipe: Optional[dict[Products, Decimal]] = None, /) -> None:
        self.base_yield = base_yield
        self.has_recipe = False

        if recipe is not None:
            total_proportion = sum(recipe.values())

            assert isclose(total_proportion, 1)

            self.recipe = recipe
            self.has_recipe = True

class Techs(Enum):
    """ Index of all technologies available """

    EXTRACTION = auto()
    CRAFTING = auto()
    MILLING = auto()

class Products(Enum):
    """ Index of all products available """

    WHEAT = auto()
    IRON = auto()
    FLOUR = auto()

    @property
    def techs(self) -> dict[Techs, Technology]:

        match self:
            case Products.WHEAT:
                return {Techs.EXTRACTION: Technology(D('4.267'))}

            case Products.IRON:
                return {Techs.EXTRACTION: Technology(D('1.723'))}

            case Products.FLOUR:
                return {Techs.CRAFTING: Technology(D('2.5'), {Products.WHEAT: D('0.8'), Products.IRON: D('0.2')}),
                        Techs.MILLING: Technology(D('3.5'), {Products.WHEAT: D('0.65'), Products.IRON: D('0.35')})}

@dataclass(order=True)
class Good(Group["Good"], amount_attr='amount'):
    """
    Do not instantiate. Use the `create_good` factory function.

    Subclass of the `Group` abstract class. This is a dataclass that represents physical products- or goods.
    Every `Good` object is associated with a `Product`, and is therefore associated with possible production technologies and
    a unique name.
    """

    product: Products
    amount: Decimal = field(compare=True)

    @property
    def name(self) -> str:
        return self.product.name.title()
    
    def _scrutinize(self, __value: Good | Decimal, *, sub=False, mul=False, div=False) -> None:
        if not isinstance(__value, (Good, Decimal)):
            raise TypeError(f'Cannot perform math between `Good` and `{type(__value).__name__}`.')
        
        elif isinstance(__value, Decimal):
            return super()._scrutinize(__value, sub=sub, mul=mul, div=div)
        
        elif __value.product != self.product:
            raise ValueError(f'Cannot perform arithmetic operations between two different products.')
            
        elif sub and __value.amount > self.amount:
            raise NegativeAmountError(f'Taking {__value} from {self} results in negative amount.')

    def _iadd(self, __value: Good) -> None:
        self.amount += __value.amount

    def _isub(self, __value: Good) -> None:
        self.amount -= __value.amount

def create_good(product: Products, amount: num = D(0)):
    """ Checks and transforms the arguments and returns a correctly instantiated `Good` object. """

    if not isinstance(product, Products):
        raise TypeError(f'The `product` parameter does not accept `{type(product).__name__}` type.')
    
    amount = D(amount)

    if amount < D(0):
        raise NegativeAmountError
    
    return Good(product, amount)

def good_factory(product: Products, /) -> Callable[..., Good]:
    """ 
    Returns a partial function that returns a `Good` object of the passed argument's product.
    The returned function takes in only an amount.
    """

    return partial(create_good, product)

class Stock(Dyct[Products, Good], factory=staticmethod(create_good)):
    """
    Do not instantiate. Use the `create_stock` factory function.

    Subclass of the abstract `Dyct` class. Represents a collection of goods.
    """

    def _scrutinize(self, __key: Products) -> None:
        if not isinstance(__key, Products):
            raise TypeError(f'Cannot use type `{type(__key).__name__}` as a key.')

    def _iadd(self, __value: Stock | Good):
        if isinstance(__value, Stock):
            for product, good in __value.items():
                self[product] += good
        
        elif isinstance(__value, Good):
            self[__value.product] += __value
        
        else:
            raise TypeError(f'Cannot sum type `Good` and type `{type(__value).__name__}`.')

    def _isub(self, __value: Stock | Good):
        if isinstance(__value, Stock):
            for product, good in __value.items():
                self[product] -= good
        
        elif isinstance(__value, Good):
            self[__value.product] -= __value
        
        else:
            raise TypeError(f'Cannot subtract type `Good` and type `{type(__value).__name__}`.')

    def reset_to(self, __value: Stock, /) -> None:
        for key in self.copy().keys():
            self[key] = __value[key]

def create_stock(init_dict: Optional[dict[Products, num]] = None, /):
    """ Transforms the passed arguments and returns a correctly instantiated `Stock` object. """

    if init_dict is None:
        return Stock({})
    
    return Stock({key: create_good(key, value) for key, value in init_dict.items()})
    
def stock_factory(*products: Products) -> Callable[..., Stock]:
    """
    Returns a function with specific products binded to it. Calling this returned function with a specific sequence of amounts,
    will return a `Stock` object with containing the products specified on the factory function with the quantities 
    specified in the returned function.
    """

    if any(product not in Products for product in products):
        raise TypeError(f'The products parameter only accepts members of `Products`.')
    
    def inner(*amounts: Decimal | int | float | str):        
        return create_stock({product: amount for product, amount in zip(products, amounts)})

    return inner
