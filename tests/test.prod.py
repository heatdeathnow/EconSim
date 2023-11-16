from parameterized import parameterized  # type: ignore
from typing import Optional, Sequence
from unittest import TestCase, main
from pathlib import Path
from sys import path

if __name__ == '__main__':
    tests_path = Path(__file__).parent
    project_path = (tests_path / '..').resolve()
    path.append(str(project_path))

from prod import Extractor, Workforce, extractor_factory, workforce_factory
from pop import Jobs, Pop, pop_factory
from goods import Goods, Stockpile

class TestWorkforce(TestCase):

    @parameterized.expand([
        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         {Jobs.FARMER: pop_factory(0, Stockpile(), Jobs.FARMER), Jobs.SPECIALIST: pop_factory(0, Stockpile(), Jobs.SPECIALIST)},
          110),
        
        ({Jobs.FARMER: 100},
         {Jobs.FARMER: pop_factory(0, Stockpile(), Jobs.FARMER)},
          100),
        
        ({Jobs.FARMER: 0},
         {Jobs.FARMER: pop_factory(0, Stockpile(), Jobs.FARMER)},
          100, ValueError),
        
        ({Jobs.FARMER: -100},
         {Jobs.FARMER: pop_factory(0, Stockpile(), Jobs.FARMER)},
          100, ValueError),
        
        ({'farmer': 0},
         {Jobs.FARMER: pop_factory(0, Stockpile(), Jobs.FARMER)},
          100, TypeError),
        ])
    def test_init_no_pops(self, needed: dict[Jobs, int | float], 
                          expected_pops: dict[Jobs, Pop], 
                          expected_capacity: int | float,
                          expected_raises: Optional[type[Exception]] = None):
        
        if expected_raises:
            with self.assertRaises(expected_raises):
                workforce_factory(needed, Stockpile())

        else:
            workforce = workforce_factory(needed, Stockpile())

            self.assertEqual(len(workforce.pops), len(expected_pops))
            for real_job, expected_job in zip(workforce.pops, expected_pops):
                self.assertEqual(real_job, expected_job)
            
            self.assertEqual(workforce.capacity, expected_capacity)
            self.assertEqual(workforce.size, 0)
    
    @parameterized.expand([
        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [pop_factory(50, Stockpile(), Jobs.FARMER), pop_factory(50, Stockpile(), Jobs.SPECIALIST)],
         110, 100),

        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [pop_factory(60, Stockpile(), Jobs.FARMER), pop_factory(50, Stockpile(), Jobs.SPECIALIST)],
         110, 110),
        
        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [pop_factory(50, Stockpile(), Jobs.FARMER), pop_factory(50, Stockpile(), Jobs.MINER)],
         0, 0, ValueError),

        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [pop_factory(61, Stockpile(), Jobs.FARMER), pop_factory(50, Stockpile(), Jobs.SPECIALIST)],
         0, 0, ValueError)
        ])
    def test_init_pops(self, needed: dict[Jobs, int | float],
                       pops: Sequence[Pop], 
                       expected_capacity: int | float, 
                       expected_size: int | float, 
                       expected_raises: Optional[type[Exception]] = None):
        if expected_raises:
            with self.assertRaises(expected_raises):
                workforce_factory(needed, Stockpile(), pops)

        else:
            workforce = workforce_factory(needed, Stockpile(), pops)
            self.assertEqual(workforce.capacity, expected_capacity)
            self.assertEqual(workforce.size, expected_size)

    @parameterized.expand([
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
                           1.0),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(100, Stockpile(), Jobs.FARMER)]),
                           0.5),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(50, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
                           0.75),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
                           0.50),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile()),
                           0.0),
        ])
    def test_efficiency(self, workforce: Workforce, expected_efficiency: float):
        self.assertAlmostEqual(workforce.efficiency, expected_efficiency)

    @parameterized.expand([
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile()),
         {Jobs.FARMER: 100, Jobs.SPECIALIST: 10}),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [pop_factory(100, Stockpile(), Jobs.FARMER)]),
         {Jobs.SPECIALIST: 10}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
         {Jobs.FARMER: 100}),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), 
                           [pop_factory(50, Stockpile(), Jobs.FARMER), pop_factory(5, Stockpile(), Jobs.SPECIALIST)]),
         {Jobs.FARMER: 50, Jobs.SPECIALIST: 5}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), 
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]), {}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [pop_factory(105, Stockpile(), Jobs.FARMER)]),
         {Jobs.SPECIALIST: 5}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [pop_factory(20, Stockpile(), Jobs.SPECIALIST)]),
         {Jobs.FARMER: 90})
        ])
    def test_labor_demand(self, workforce: Workforce, expected_demand: dict[Jobs, int | float]):
        self.assertEqual(len(workforce.labor_demand()), len(expected_demand))

        for (real_job, real_amount), (expected_job, expected_amount) in zip(workforce.labor_demand().items(), expected_demand.items()):
            self.assertEqual(real_job, expected_job)
            self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        #  LOWER: {Goods.WHEAT: 1.0}
        # MIDDLE: {Goods.WHEAT: 2.0, Goods.IRON: 1.0}

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile({Goods.WHEAT: 100 + 20, Goods.IRON: 10})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(50, Stockpile(), Jobs.FARMER), pop_factory(5, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile({Goods.WHEAT: 50 + 10, Goods.IRON: 5})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [pop_factory(100, Stockpile(), Jobs.FARMER)]), 
         Stockpile({Goods.WHEAT: 100})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile()), 
         Stockpile())
        ])
    def test_nominal_goods_demand(self, workforce: Workforce, expected_demand: Stockpile):
        self.assertEqual(len(workforce.nominal_goods_demand), len(expected_demand))

        for (real_good, real_amount), (expected_good, expected_amount) in zip(workforce.nominal_goods_demand.items(), expected_demand.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)
    
    @parameterized.expand([
        #  LOWER: {Goods.WHEAT: 1.0}
        # MIDDLE: {Goods.WHEAT: 2.0, Goods.IRON: 1.0}

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile({Goods.WHEAT: 100 + 20, Goods.IRON: 10})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.WHEAT: 25, Goods.IRON: 2}),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile({Goods.WHEAT: 95, Goods.IRON: 8})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.WHEAT: 120, Goods.IRON: 10}),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile()),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.WHEAT: 500, Goods.IRON: 500}),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile()),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.IRON: 500}),
                           [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
        Stockpile({Goods.WHEAT: 120})),
        ])
    def test_effective_goods_demand(self, workforce: Workforce, expected_demand: Stockpile):
        self.assertEqual(len(workforce.effective_goods_demand), len(expected_demand))

        for (real_good, real_amount), (expected_good, expected_amount) in zip(workforce.effective_goods_demand.items(), expected_demand.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

class TestExtractor(TestCase):
    
    @parameterized.expand([
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile()),
            Goods.WHEAT, Stockpile()), Stockpile()),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [pop_factory(100, Stockpile(), Jobs.FARMER)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 100 * 0.5})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [pop_factory(100, Stockpile(), Jobs.FARMER), pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 110 * 1})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [pop_factory(10, Stockpile(), Jobs.SPECIALIST)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 10 * 0.5})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [pop_factory(50, Stockpile(), Jobs.FARMER), pop_factory(5, Stockpile(), Jobs.SPECIALIST)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 55 * 0.5})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [pop_factory(75, Stockpile(), Jobs.FARMER), pop_factory(5, Stockpile(), Jobs.SPECIALIST)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 80 * 0.625})),
    ])
    def test_produces(self, extractor: Extractor, expected: Stockpile):
        produced = extractor.produce()

        self.assertEqual(len(produced), len(expected))
        for (real_good, real_amount), (expected_good, expected_amount) in zip(produced.items(), expected.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

if __name__ == '__main__':
    main()