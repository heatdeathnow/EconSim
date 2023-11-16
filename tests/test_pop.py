from parameterized import parameterized  # type: ignore
from unittest import TestCase, main
from typing import Optional
from pathlib import Path
from sys import path


if __name__ == '__main__':
    tests_path = Path(__file__).parent
    project_path = (tests_path / '..').resolve()
    path.append(str(project_path))

from pop import Pop, Jobs, Strata, pop_factory
from goods import Goods, Stockpile

############################################################################################################################################

class TestPop(TestCase):

    # testing `pop_factory` function and `Pop`'s `__init__` method. 
    @parameterized.expand([
        (100, Stockpile(), Jobs.FARMER, None, (100, Jobs.FARMER, Strata.LOWER)),
        (100, Stockpile(), Jobs.MINER, None, (100, Jobs.MINER, Strata.LOWER)),
        (100, Stockpile(), Jobs.SPECIALIST, None, (100, Jobs.SPECIALIST, Strata.MIDDLE)),

        (100, Stockpile(), None, Strata.LOWER, (100, None, Strata.LOWER)),
        (100, Stockpile(), None, Strata.MIDDLE, (100, None, Strata.MIDDLE)),
        (100, Stockpile(), None, Strata.UPPER, (100, None, Strata.UPPER)),

        (100, Stockpile(), None, None, ValueError),
        (-100, Stockpile(), None, Strata.LOWER, ValueError),
        (-100, Stockpile(), Jobs.SPECIALIST, Strata.LOWER, ValueError),

        (100, Stockpile({Goods.WHEAT: 100}), Jobs.FARMER, None, (100, Jobs.FARMER, Strata.LOWER)),
        (100, Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}), Jobs.FARMER, None, (100, Jobs.FARMER, Strata.LOWER)),
    ])
    def test_init(self,
                size: int | float,
                stockpile: Stockpile,
                job: Jobs, 
                stratum: Strata,
                expected: type[Exception] | tuple[int | float, Jobs, Strata]) -> None:
        
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                pop_factory(size, stockpile, job, stratum)

        else:
            pop = pop_factory(size, stockpile, job, stratum)

            self.assertEqual(pop.size, expected[0])
            self.assertEqual(pop.job, expected[1])
            self.assertEqual(pop.stratum, expected[2])

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (pop_factory(100, Stockpile(), Jobs.FARMER), {Goods.WHEAT: 100}),
        (pop_factory(100, Stockpile(), Jobs.MINER), {Goods.WHEAT: 100}),
        (pop_factory(100, Stockpile(), Jobs.SPECIALIST), {Goods.WHEAT: 200, Goods.IRON: 100}),

        (pop_factory(50.55, Stockpile(), Jobs.FARMER), {Goods.WHEAT: 50.55}),
        (pop_factory(50.55, Stockpile(), Jobs.SPECIALIST), {Goods.WHEAT: 101.1, Goods.IRON: 50.55}),
    ])
    def test_consumption(self, pop: Pop, expected: dict[Goods, int | float]) -> None:
        self.assertEqual(len(pop.consumption), len(expected))

        for (real_good, real_amount), (expected_good, expected_amount) in zip(pop.consumption.items(), expected.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (pop_factory(100, Stockpile({Goods.WHEAT: 100}), Jobs.FARMER), 1.0),
        (pop_factory(100, Stockpile({Goods.WHEAT: 50}), Jobs.FARMER), 0.5),
        (pop_factory(100, Stockpile(), Jobs.FARMER), 0.0),

        (pop_factory(100, Stockpile({Goods.WHEAT: 200, Goods.IRON: 100}), Jobs.SPECIALIST, ), 1.0),
        (pop_factory(100, Stockpile({Goods.WHEAT: 200}), Jobs.SPECIALIST), 0.5),
        (pop_factory(100, Stockpile({Goods.IRON: 100}), Jobs.SPECIALIST), 0.5),
        (pop_factory(100, Stockpile({Goods.WHEAT: 100, Goods.IRON: 50}), Jobs.SPECIALIST), 0.5),
        (pop_factory(100, Stockpile(), Jobs.SPECIALIST), 0.0),
    ])
    def test_welfare(self, pop: Pop, expected: float) -> None:
        self.assertAlmostEqual(pop.welfare, expected)

    @parameterized.expand([
        # Welfare_threshold = 0.75; growth_rate = 0.05; promote_rate = 0.01
        (pop_factory(100, Stockpile({Goods.WHEAT: 100}), Jobs.FARMER), 105, pop_factory(1, Stockpile(), None, Strata.MIDDLE), Stockpile()),
        (pop_factory(100, Stockpile({Goods.WHEAT: 75}), Jobs.FARMER), 105, pop_factory(1, Stockpile(), None, Strata.MIDDLE), Stockpile()),
        (pop_factory(100, Stockpile({Goods.WHEAT: 74}), Jobs.FARMER), 95, None, Stockpile()),

        (pop_factory(100, Stockpile({Goods.WHEAT: 200, Goods.IRON: 100}), Jobs.SPECIALIST), 105, None, Stockpile()),
        (pop_factory(100, Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}), Jobs.SPECIALIST), 105, None, Stockpile()),
        (pop_factory(100, Stockpile({Goods.WHEAT: 50, Goods.IRON: 50}), Jobs.SPECIALIST), 95, None, Stockpile()),

        (pop_factory(100, Stockpile({Goods.WHEAT: 200}), Jobs.FARMER), 105, pop_factory(1, Stockpile(), None, Strata.MIDDLE), 
        Stockpile({Goods.WHEAT: 100})),
        (pop_factory(100, Stockpile({Goods.WHEAT: 300, Goods.IRON: 150}), Jobs.SPECIALIST), 105, None, 
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
