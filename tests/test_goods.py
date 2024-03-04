from decimal import Decimal, getcontext
from unittest import skip
from parameterized import parameterized
from source.exceptions import NegativeAmountError
from source.goods import Good, Products, Stock, good_factory, stock_factory
from tests import GoodsMixIn
D = getcontext().create_decimal


WHEAT = Products.WHEAT
IRON = Products.IRON
FLOUR = Products.FLOUR

wheat_fac = good_factory(WHEAT)
iron_fac = good_factory(IRON)
flour_fac = good_factory(FLOUR)

wheat_stock_fac = stock_factory(WHEAT)
iron_stock_fac = stock_factory(IRON)
wheat_iron_stock_fac = stock_factory(WHEAT, IRON)

class TestGood(GoodsMixIn):

    @parameterized.expand([
        (wheat_fac(100), wheat_fac(100), wheat_fac(200)),
        (wheat_fac(100), wheat_fac(55.55), wheat_fac(155.55)),

        (wheat_fac(100), iron_fac(100), ValueError),
    ])
    def test_add(self, good1: Good, good2: Good, expected: type[Exception] | Good):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, good1.__add__, good2)

        else:
            good = good1 + good2
            good1 += good2

            self.assert_goods_equal(good, expected)
            self.assert_goods_equal(good1, expected)

    @parameterized.expand([
        (wheat_fac(200), wheat_fac(100), wheat_fac(100)),
        (wheat_fac(100), wheat_fac(55.55), wheat_fac(44.45)),
        (wheat_fac(100), wheat_fac(100), wheat_fac()),

        (wheat_fac(100), iron_fac(50), ValueError),
        (wheat_fac(100), wheat_fac(150), NegativeAmountError),
        ])
    def test_sub(self, good1: Good, good2: Good, expected: type[Exception] | Good):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, good1.__sub__, good2)

        else:
            good = good1 - good2
            good1 -= good2

            self.assert_goods_equal(good, expected)
            self.assert_goods_equal(good1, expected)

    @parameterized.expand([
        (wheat_fac(100), D(2), wheat_fac(200)),
        (wheat_fac(100), D(0.5), wheat_fac(50)),
        (iron_fac(100), D(5), iron_fac(500)),

        (wheat_fac(100), D(0), wheat_fac()),
        (wheat_fac(100), D(-1), NegativeAmountError),
    ])
    def test_mul(self, good1: Good, mult: Decimal, expected: type[Exception] | Good):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, good1.__mul__, mult)

        else:
            good = good1 * mult
            self.assert_goods_equal(good, expected)

    @parameterized.expand([
        (wheat_fac(100), D(2), wheat_fac(50)),
        (wheat_fac(100), D(0.5), wheat_fac(200)),
        (iron_fac(100), D(5), iron_fac(20)),

        (wheat_fac(100), D(0), ZeroDivisionError),
        (wheat_fac(100), D(-1), NegativeAmountError),
    ])
    def test_div(self, good1: Good, div: Decimal, expected: type[Exception] | Good):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, good1.__truediv__, div)

        else:
            good = good1 / div
            self.assert_goods_equal(good, expected)

class TestStockpile(GoodsMixIn):

    @parameterized.expand([
        (wheat_stock_fac(), WHEAT, wheat_fac(100), wheat_stock_fac(100)),
        (wheat_stock_fac(100), WHEAT, wheat_fac(50), wheat_stock_fac(50)),
        (wheat_stock_fac(100), WHEAT, wheat_fac(), wheat_stock_fac()),

        (wheat_stock_fac(), 'WHEAT', wheat_fac(100), TypeError),
    ])
    def test_set_item(self, stockpile: Stock, key: Products, value: Good, expected: type[Exception] | Stock):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__setitem__, key, value)

        else:
            stockpile[key] = value
            self.assert_stocks_equal(expected, stockpile)

    @parameterized.expand([
        (wheat_stock_fac(100), WHEAT, wheat_fac(100)),
        (wheat_stock_fac(), WHEAT, wheat_fac()),
        (wheat_stock_fac(), 'wheat_fac', TypeError),
    ])
    def test_get_item(self, stockpile: Stock, key: Products, expected: type[Exception] | Good):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__getitem__, key)

        else:
            good = stockpile[key]
            self.assert_goods_equal(good, expected)

    @parameterized.expand([
        (wheat_stock_fac(10), wheat_fac(10), wheat_stock_fac(20)),
        (wheat_iron_stock_fac(10, 10), iron_fac(10), wheat_iron_stock_fac(10, 20)),
        
        (wheat_stock_fac(), wheat_fac(10), wheat_stock_fac(10)),
        (wheat_stock_fac(10), iron_fac(10), wheat_iron_stock_fac(10, 10)),
        
        (wheat_stock_fac(10), wheat_iron_stock_fac(10, 10), wheat_iron_stock_fac(20, 10)),
        (wheat_iron_stock_fac(5, 5.5), iron_stock_fac(5), wheat_iron_stock_fac(5, 10.5)),

        (wheat_stock_fac(), 10, TypeError),
    ])
    def test_add(self, stockpile: Stock, item: Good | Stock, expected: type[Exception] | Stock):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__add__, item)
        
        else:
            new = stockpile + item
            stockpile += item

            self.assert_stocks_equal(new, expected)
            self.assert_stocks_equal(stockpile, expected)

    @parameterized.expand([
        (wheat_stock_fac(20), wheat_fac(10), wheat_stock_fac(10)),
        (wheat_stock_fac(10), wheat_fac(10), wheat_stock_fac()),
        (wheat_iron_stock_fac(10, 10), iron_fac(10), wheat_stock_fac(10)),
        
        (wheat_stock_fac(20), wheat_stock_fac(10), wheat_stock_fac(10)),
        (wheat_stock_fac(20), wheat_stock_fac(20), wheat_stock_fac()),
        (wheat_iron_stock_fac(10, 10), wheat_stock_fac(10), iron_stock_fac(10)),
        (wheat_iron_stock_fac(10, 10), wheat_iron_stock_fac(5, 3), wheat_iron_stock_fac(5, 7)),
        (wheat_iron_stock_fac(10, 10), wheat_iron_stock_fac(10, 5), iron_stock_fac(5)),
        (wheat_iron_stock_fac(10, 10), wheat_iron_stock_fac(10, 10), wheat_stock_fac()),

        (wheat_stock_fac(), wheat_fac(10), NegativeAmountError),
        (wheat_stock_fac(10), iron_fac(10), NegativeAmountError),
        (wheat_stock_fac(), 10, TypeError),
    ])
    def test_sub(self, stockpile: Stock, item: Good | Stock, expected: type[Exception] | Stock):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__sub__, item)
        
        else:
            new = stockpile - item
            stockpile -= item

            self.assert_stocks_equal(new, expected)
            self.assert_stocks_equal(stockpile, expected)

    @parameterized.expand([
        (wheat_stock_fac(100), D(2), wheat_stock_fac(200)),
        (wheat_stock_fac(0.5), D(2), wheat_stock_fac(1)),
        (wheat_iron_stock_fac(100, 50), D(2), wheat_iron_stock_fac(200, 100)),
        (wheat_stock_fac(100), D(1), wheat_stock_fac(100)),

        (wheat_stock_fac(100), D(0.5), wheat_stock_fac(50)),
        (wheat_iron_stock_fac(100, 50), D(0.5), wheat_iron_stock_fac(50, 25)),

        (wheat_iron_stock_fac(100, 50), D(0), wheat_stock_fac()),

        (wheat_iron_stock_fac(100, 50), D(-1), NegativeAmountError),
        (wheat_iron_stock_fac(100, 50), 'a', TypeError),
    ])
    def test_mul(self, stockpile: Stock, multiplier: Decimal, expected: type[Exception] | Stock):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__mul__, multiplier)
        
        else:
            multiplied = stockpile * multiplier
            self.assert_stocks_equal(multiplied, expected)

    @parameterized.expand([
        (wheat_stock_fac(100), D(2), wheat_stock_fac(50)),
        (wheat_stock_fac(100), D(3), wheat_stock_fac('33.333')),

        (wheat_iron_stock_fac(100, 50), D(2), wheat_iron_stock_fac(50, 25)),
        (wheat_iron_stock_fac(100, 50), D(3), wheat_iron_stock_fac('33.333', '16.66666666666666')),

        (wheat_stock_fac(100), D(0), ZeroDivisionError),
        (wheat_stock_fac(100), D(-1), NegativeAmountError),
        (wheat_stock_fac(100), 'test', TypeError),
    ])
    def test_div(self, stockpile: Stock, divisor: Decimal, expected: type[Exception] | Stock):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__truediv__, divisor)
        
        else:
            divided = stockpile / divisor
            self.assert_stocks_equal(divided, expected)

    @parameterized.expand([
        (wheat_iron_stock_fac(100, 100), wheat_stock_fac(10)),
    ])
    def test_reset_to(self, stockpile: Stock, resetor: Stock):
        id1 = id(stockpile)
        stockpile.reset_to(resetor)

        self.assert_stocks_equal(stockpile, resetor)
        self.assertEqual(id1, id(stockpile))
