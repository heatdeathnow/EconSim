from decimal import ROUND_HALF_DOWN, Context, Decimal, DivisionByZero, InvalidOperation
from typing import TYPE_CHECKING, Literal
D = Decimal

ROUNDING = 3
PRECISION = D(10) ** -ROUNDING

if TYPE_CHECKING:
    from .pop import Strata, Jobs
    from goods import Products

type num = Decimal | int | float | str
type unemployed_key = tuple[Strata, Literal[Jobs.UNEMPLOYED]]
type pop_dict = dict[Jobs, num]
type goods_dict = dict[Products, num]

