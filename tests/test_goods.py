from parameterized import parameterized
from unittest import TestCase
from source.exceptions import NegativeAmountError
from source.goods import Goods, Stockpile

class TestStockpile(TestCase):
    
    @parameterized.expand([
        ({Goods.WHEAT: 100}, Stockpile({Goods.WHEAT: 100})),
        ({Goods.WHEAT: 100, Goods.IRON: 100}, Stockpile({Goods.WHEAT: 100, Goods.IRON: 100})),

        ({'wheat': 100, 'iron': 100}, TypeError),
        ({Goods.WHEAT: -100}, NegativeAmountError),
        ({Goods.WHEAT: 100, Goods.IRON: -100}, NegativeAmountError),

        ({Goods.WHEAT: 0}, Stockpile()),
        ({Goods.WHEAT: 100, Goods.IRON: 0}, Stockpile({Goods.WHEAT: 100})),
    ])
    def test_init(self, kwargs: dict, expected: type[Exception] | Stockpile):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                Stockpile(kwargs)

        else:
            stockpile = Stockpile(kwargs)

            self.assertEqual(len(stockpile), len(expected))
            for (real_good, real_amount), (expected_good, expected_amount) in zip(stockpile.items(), expected.items()):
                self.assertEqual(real_good, expected_good)
                self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        (Stockpile(), (Goods.WHEAT, 100), Stockpile({Goods.WHEAT: 100})),
        (Stockpile({Goods.WHEAT: 100}), (Goods.WHEAT, 50), Stockpile({Goods.WHEAT: 50})),
        (Stockpile({Goods.WHEAT: 100}), (Goods.WHEAT, 0), Stockpile()),
        (Stockpile(), (Goods.WHEAT, -100), NegativeAmountError),
    ])
    def test_set_item(self, stockpile: Stockpile, item: tuple[Goods, int | float], expected: type[Exception] | Stockpile):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                stockpile[item[0]] = item[1]

        else:
            stockpile[item[0]] = item[1]

            self.assertEqual(len(stockpile), len(expected))
            for (real_good, real_amount), (expected_good, expected_amount) in zip(stockpile.items(), expected.items()):
                self.assertEqual(real_good, expected_good)
                self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        (Stockpile({Goods.WHEAT: 100}), Goods.WHEAT, 100),
        (Stockpile(), Goods.WHEAT, 0.0),
        (Stockpile(), 'wheat', TypeError),
    ])
    def test_get_item(self, stockpile: Stockpile, item: Goods, expected: type[Exception] | int | float):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                stockpile[item]

        else:
            value = stockpile[item]
            self.assertEqual(value, expected)

    @parameterized.expand([
        (Stockpile({Goods.WHEAT: 10}), (Goods.WHEAT, 10), Stockpile({Goods.WHEAT: 20})),
        (Stockpile({Goods.WHEAT: 10, Goods.IRON: 10}), (Goods.IRON, 10), Stockpile({Goods.WHEAT: 10, Goods.IRON: 20})),
        
        (Stockpile(), (Goods.WHEAT, 10), Stockpile({Goods.WHEAT: 10})),
        (Stockpile({Goods.WHEAT: 10}), (Goods.IRON, 10), Stockpile({Goods.WHEAT: 10, Goods.IRON: 10})),
        
        (Stockpile(), ('wheat', 10), TypeError),
    ])
    def test_add(self, stockpile: Stockpile, item: tuple[Goods, int | float], expected: type[Exception] | Stockpile):

        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                stockpile += Stockpile({item[0]: item[1]})
                stockpile[item[0]] + item[1]
        
        else:

            new = stockpile + Stockpile({item[0]: item[1]})
            stockpile[item[0]] += item[1]

            self.assertEqual(len(stockpile), len(expected))
            self.assertEqual(len(new), len(expected))

            for good, amount in expected.items():
                self.assertEqual(amount, new[good])
                self.assertEqual(amount, stockpile[good])

    @parameterized.expand([
        (Stockpile({Goods.WHEAT: 20}), (Goods.WHEAT, 10), Stockpile({Goods.WHEAT: 10})),
        (Stockpile({Goods.WHEAT: 10}), (Goods.WHEAT, 10), Stockpile()),
        (Stockpile({Goods.WHEAT: 10, Goods.IRON: 10}), (Goods.IRON, 10), Stockpile({Goods.WHEAT: 10})),
        
        (Stockpile(), (Goods.WHEAT, 10), NegativeAmountError),
        (Stockpile({Goods.WHEAT: 10}), (Goods.IRON, 10), NegativeAmountError),
        
        (Stockpile(), ('wheat', 10), TypeError),
    ])
    def test_sub(self, stockpile: Stockpile, item: tuple[Goods, int | float], expected: type[Exception] | Stockpile):

        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                stockpile -= Stockpile({item[0]: item[1]})
                stockpile[item[0]] - item[1]
        
        else:

            new = stockpile - Stockpile({item[0]: item[1]})
            stockpile[item[0]] -= item[1]

            self.assertEqual(len(stockpile), len(expected))
            self.assertEqual(len(new), len(expected))
            
            for good, amount in expected.items():
                self.assertEqual(amount, new[good])
                self.assertEqual(amount, stockpile[good])
    
    @parameterized.expand([
        (Stockpile({Goods.WHEAT: 100}), 2, Stockpile({Goods.WHEAT: 50})),
        (Stockpile({Goods.WHEAT: 100}), 3, Stockpile({Goods.WHEAT: 33.33333333})),

        (Stockpile({Goods.WHEAT: 100, Goods.IRON: 50}), 2, Stockpile({Goods.WHEAT: 50, Goods.IRON: 25})),
        (Stockpile({Goods.WHEAT: 100, Goods.IRON: 50}), 3, Stockpile({Goods.WHEAT: 33.33333333, Goods.IRON: 16.66666666})),

        (Stockpile({Goods.WHEAT: 100}), 0, ZeroDivisionError),
        (Stockpile({Goods.WHEAT: 100}), -1, NegativeAmountError),
        (Stockpile({Goods.WHEAT: 100}), 'test', TypeError),
    ])
    def test_div(self, stockpile: Stockpile, divisor: int | float, expected: type[Exception] | Stockpile):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, stockpile.__truediv__, divisor)
        
        else:
            divided = stockpile / divisor

            self.assertEqual(len(divided), len(expected))

            for good, amount in expected.items():
                self.assertAlmostEqual(amount, divided[good])
