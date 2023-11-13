from parameterized import parameterized
from unittest import TestCase, main
from pathlib import Path
from sys import path


if __name__ == '__main__':
    tests_path = Path(__file__).parent
    project_path = (tests_path / '..').resolve()
    path.append(str(project_path))

from prod import Goods, Stockpile

class TestStockpile(TestCase):
    
    @parameterized.expand([
        ({Goods.WHEAT: 100}, Stockpile({Goods.WHEAT: 100})),
        ({Goods.WHEAT: 100, Goods.IRON: 100}, Stockpile({Goods.WHEAT: 100, Goods.IRON: 100})),

        ({'wheat': 100, 'iron': 100}, TypeError),
        ({Goods.WHEAT: -100}, ValueError),
        ({Goods.WHEAT: 100, Goods.IRON: -100}, ValueError),

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
        (Stockpile(), (Goods.WHEAT, -100), ValueError),
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
        
        (Stockpile({Goods.WHEAT: 10}), (Goods.WHEAT, -10), Stockpile()),
        (Stockpile({Goods.WHEAT: 10, Goods.IRON: 10}), (Goods.WHEAT, -10), Stockpile({Goods.IRON: 10})),

        (Stockpile(), (Goods.WHEAT, -10), ValueError),
        (Stockpile(), ('wheat', 10), TypeError),
    ])
    def test_add(self, stockpile: Stockpile, item: tuple[Goods, int | float], expected: type[Exception] | Stockpile):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                stockpile[item[0]] += item[1]
        
        else:
            stockpile[item[0]] += item[1]

            self.assertEqual(len(stockpile), len(expected))
            for (real_good, real_amount), (expected_good, expected_amount) in zip(stockpile.items(), expected.items()):
                self.assertEqual(real_good, expected_good)
                self.assertAlmostEqual(real_amount, expected_amount)

if __name__ == '__main__':
    main()
