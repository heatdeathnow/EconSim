from parameterized import parameterized
from unittest import TestCase, main
from typing import Optional
from pathlib import Path
from sys import path


if __name__ == '__main__':
    tests_path = Path(__file__).parent
    project_path = (tests_path / '..').resolve()
    path.append(str(project_path))

from pop import Pop, Jobs, Strata, pop_factory
from prod import Goods, Stockpile

############################################################################################################################################

class TestPop(TestCase):

    # testing `pop_factory` function and `Pop`'s `__init__` method. 
    @parameterized.expand([
        (100, Jobs.FARMER, None, None, (100, Jobs.FARMER, Strata.LOWER)),
        (100, Jobs.MINER, None, None, (100, Jobs.MINER, Strata.LOWER)),
        (100, Jobs.SPECIALIST, None, None, (100, Jobs.SPECIALIST, Strata.MIDDLE)),

        (100, None, Strata.LOWER, None, (100, None, Strata.LOWER)),
        (100, None, Strata.MIDDLE, None, (100, None, Strata.MIDDLE)),
        (100, None, Strata.UPPER, None, (100, None, Strata.UPPER)),

        (100, None, None, None, ValueError),
        (-100, None, Strata.LOWER, None, ValueError),
        (-100, Jobs.SPECIALIST, Strata.LOWER, None, ValueError),

        (100, Jobs.FARMER, None, Stockpile({Goods.WHEAT: 100}), (100, Jobs.FARMER, Strata.LOWER)),
        (100, Jobs.FARMER, None, Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}), (100, Jobs.FARMER, Strata.LOWER)),
    ])
    def test_init(self,
                size: int | float,
                job: Jobs, stratum: Strata,
                stockpile: Stockpile,
                expected: type[Exception] | tuple[int | float, Jobs, Strata]) -> None:
        
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                pop_factory(size, job, stratum, stockpile)

        else:
            pop = pop_factory(size, job, stratum, stockpile)

            self.assertEqual(pop.size, expected[0])
            self.assertEqual(pop.job, expected[1])
            self.assertEqual(pop.stratum, expected[2])

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (pop_factory(100, Jobs.FARMER), {Goods.WHEAT: 100}),
        (pop_factory(100, Jobs.MINER), {Goods.WHEAT: 100}),
        (pop_factory(100, Jobs.SPECIALIST), {Goods.WHEAT: 200, Goods.IRON: 100}),

        (pop_factory(50.55, Jobs.FARMER), {Goods.WHEAT: 50.55}),
        (pop_factory(50.55, Jobs.SPECIALIST), {Goods.WHEAT: 101.1, Goods.IRON: 50.55}),
    ])
    def test_consumption(self, pop: Pop, expected: dict[Goods, int | float]) -> None:
        self.assertEqual(len(pop.consumption), len(expected))

        for (real_good, real_amount), (expected_good, expected_amount) in zip(pop.consumption.items(), expected.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (pop_factory(100, Jobs.FARMER, stockpile=Stockpile({Goods.WHEAT: 100})), 1.0),
        (pop_factory(100, Jobs.FARMER, stockpile=Stockpile({Goods.WHEAT: 50})), 0.5),
        (pop_factory(100, Jobs.FARMER), 0.0),

        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 200, Goods.IRON: 100})), 1.0),
        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 200})), 0.5),
        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.IRON: 100})), 0.5),
        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 100, Goods.IRON: 50})), 0.5),
        (pop_factory(100, Jobs.SPECIALIST), 0.0),
    ])
    def test_welfare(self, pop: Pop, expected: float) -> None:
        self.assertAlmostEqual(pop.welfare, expected)

    @parameterized.expand([
        # Welfare_threshold = 0.75; growth_rate = 0.05; promote_rate = 0.01
        (pop_factory(100, Jobs.FARMER, stockpile=Stockpile({Goods.WHEAT: 100})), 105, pop_factory(1, None, Strata.MIDDLE), Stockpile()),
        (pop_factory(100, Jobs.FARMER, stockpile=Stockpile({Goods.WHEAT: 75})), 105, pop_factory(1, None, Strata.MIDDLE), Stockpile()),
        (pop_factory(100, Jobs.FARMER, stockpile=Stockpile({Goods.WHEAT: 74})), 95, None, Stockpile()),

        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 200, Goods.IRON: 100})), 105, None, Stockpile()),
        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 100, Goods.IRON: 100})), 105, None, Stockpile()),
        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 50, Goods.IRON: 50})), 95, None, Stockpile()),

        (pop_factory(100, Jobs.FARMER, stockpile=Stockpile({Goods.WHEAT: 200})), 105, pop_factory(1, None, Strata.MIDDLE), 
        Stockpile({Goods.WHEAT: 100})),
        (pop_factory(100, Jobs.SPECIALIST, stockpile=Stockpile({Goods.WHEAT: 300, Goods.IRON: 150})), 105, None, 
        Stockpile({Goods.WHEAT: 100, Goods.IRON: 50})),
    ])
    def test_tick(self, pop: Pop, expected_size: int | float, expected_return: Optional[Pop], expected_stockpile: Stockpile) -> None:
        returned = pop.tick()

        self.assertAlmostEqual(pop.size, expected_size)

        if expected_return and returned:
            self.assertAlmostEqual(expected_return.size, returned.size)
            self.assertEqual(None, returned.job)
            self.assertEqual(expected_return.stratum, returned.stratum)
        
        elif expected_return and returned is None:
            self.fail('Expected pop promotion, but got `None`.')
        
        elif returned and expected_return is None:
            self.fail(f'Expected no pop promotion, but got {returned}.')
        
        self.assertEqual(len(pop.stockpile), len(expected_stockpile))
        for (real_good, real_amount), (expected_good, expected_amount) in zip(pop.stockpile.items(), expected_stockpile.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

if __name__ == '__main__':
    main()
