from parameterized import parameterized
from typing import Optional, Sequence
from unittest import TestCase

from pyparsing import Opt
from source.prod import CannotEmploy, Extractor, Workforce, extractor_factory, workforce_factory
from source.pop import Jobs, Pop, Strata, PopFactory
from source.goods import Goods, Stockpile

class TestWorkforce(TestCase):

    @parameterized.expand([
        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 0), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 0)},
          110),
        
        ({Jobs.FARMER: 100},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 0)},
          100),
        
        ({Jobs.FARMER: 0},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 0)},
          100, ValueError),
        
        ({Jobs.FARMER: -100},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 0)},
          100, ValueError),
        
        ({'farmer': 0},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 0)},
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
         [PopFactory.job(Jobs.FARMER, 50), PopFactory.job(Jobs.SPECIALIST, 50)],
         110, 100),

        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [PopFactory.job(Jobs.FARMER, 60), PopFactory.job(Jobs.SPECIALIST, 50)],
         110, 110),
        
        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [PopFactory.job(Jobs.FARMER, 50), PopFactory.job(Jobs.MINER, 50)],
         0, 0, ValueError),

        ({Jobs.FARMER: 100, Jobs.SPECIALIST: 10},
         [PopFactory.job(Jobs.FARMER, 61), PopFactory.job(Jobs.SPECIALIST, 50)],
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
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
                           1.0),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [PopFactory.job(Jobs.FARMER, 100)]),
                           0.5),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [PopFactory.job(Jobs.FARMER, 50), PopFactory.job(Jobs.SPECIALIST, 10)]),
                           0.75),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [PopFactory.job(Jobs.SPECIALIST, 10)]),
                           0.50),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile()),
                           0.0),
        ])
    def test_efficiency(self, workforce: Workforce, expected_efficiency: float):
        self.assertAlmostEqual(workforce.efficiency, expected_efficiency)

    @parameterized.expand([
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile()),
         {Jobs.FARMER: 100, Jobs.SPECIALIST: 10}),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [PopFactory.job(Jobs.FARMER, 100)]),
         {Jobs.SPECIALIST: 10}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [PopFactory.job(Jobs.SPECIALIST, 10)]),
         {Jobs.FARMER: 100}),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), 
                           [PopFactory.job(Jobs.FARMER, 50), PopFactory.job(Jobs.SPECIALIST, 5)]),
         {Jobs.FARMER: 50, Jobs.SPECIALIST: 5}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), 
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]), {}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [PopFactory.job(Jobs.FARMER, 105)]),
         {Jobs.SPECIALIST: 5}),
        
        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [PopFactory.job(Jobs.SPECIALIST, 20)]),
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
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
        Stockpile({Goods.WHEAT: 100 + 20, Goods.IRON: 10})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                           [PopFactory.job(Jobs.FARMER, 50), PopFactory.job(Jobs.SPECIALIST, 5)]),
        Stockpile({Goods.WHEAT: 50 + 10, Goods.IRON: 5})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(), [PopFactory.job(Jobs.FARMER, 100)]), 
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
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
        Stockpile({Goods.WHEAT: 100 + 20, Goods.IRON: 10})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.WHEAT: 25, Goods.IRON: 2}),
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
        Stockpile({Goods.WHEAT: 95, Goods.IRON: 8})),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.WHEAT: 120, Goods.IRON: 10}),
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
        Stockpile()),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.WHEAT: 500, Goods.IRON: 500}),
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
        Stockpile()),

        (workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile({Goods.IRON: 500}),
                           [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
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
                              [PopFactory.job(Jobs.FARMER, 100)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 100 * 0.5})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.SPECIALIST, 10)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 110 * 1})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [PopFactory.job(Jobs.SPECIALIST, 10)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 10 * 0.5})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [PopFactory.job(Jobs.FARMER, 50), PopFactory.job(Jobs.SPECIALIST, 5)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 55 * 0.5})),
        
        (extractor_factory(
            workforce_factory({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}, Stockpile(),
                              [PopFactory.job(Jobs.FARMER, 75), PopFactory.job(Jobs.SPECIALIST, 5)]),
            Goods.WHEAT, Stockpile()), Stockpile({Goods.WHEAT: 1.25 * 80 * 0.625})),
    ])
    def test_produces(self, extractor: Extractor, expected: Stockpile):
        produced = extractor.produce()

        self.assertEqual(len(produced), len(expected))
        for (real_good, real_amount), (expected_good, expected_amount) in zip(produced.items(), expected.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        (extractor_factory(workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 45), PopFactory.job(Jobs.SPECIALIST, 5)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.job(Jobs.FARMER, 10),
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 55), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 5)},
         PopFactory.job(Jobs.FARMER)),

        (extractor_factory(workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 45), PopFactory.job(Jobs.SPECIALIST, 5)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.job(Jobs.SPECIALIST, 1),
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 45), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 6)},
         PopFactory.job(Jobs.SPECIALIST)),
        
        (extractor_factory(workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 45), PopFactory.job(Jobs.SPECIALIST, 5)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.stratum(Strata.LOWER, 10),
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 55), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 5)},
         PopFactory.stratum(Strata.LOWER)),
        
        (extractor_factory(workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 45), PopFactory.job(Jobs.SPECIALIST, 5)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.stratum(Strata.MIDDLE, 1),
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 45), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 6)},
         PopFactory.stratum(Strata.MIDDLE)),

        (extractor_factory(workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 45), PopFactory.job(Jobs.SPECIALIST, 5)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.job(Jobs.MINER, 10),
         ValueError, None),
        
        (extractor_factory(workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 45), PopFactory.job(Jobs.SPECIALIST, 5)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.job(Jobs.FARMER, 50),
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 90), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 5)},
         PopFactory.job(Jobs.FARMER, 5)),
        
        (extractor_factory(workforce_factory({Jobs.FARMER: 50, Jobs.MINER: 50}, Stockpile(),
                                             [PopFactory.job(Jobs.FARMER, 25), PopFactory.job(Jobs.MINER, 25)]),
                           Goods.WHEAT, Stockpile()),
         PopFactory.stratum(Strata.LOWER, 100),
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 50), Jobs.MINER: PopFactory.job(Jobs.MINER, 50)},
         PopFactory.stratum(Strata.LOWER, 50)),
    ])
    def test_employ(self, extractor: Extractor, 
                    to_employ: Pop, 
                    expected_workforce: type[Exception] | dict[Jobs, Pop], 
                    expected_returned: Pop):
        
        if isinstance(expected_workforce, type) and issubclass(expected_workforce, Exception):
            with self.assertRaises(expected_workforce):
                extractor.employ(to_employ)
        
        else:
            returned = extractor.employ(to_employ)

            self.assertEqual(returned.job, expected_returned.job)
            self.assertAlmostEqual(returned.size, expected_returned.size)

            self.assertEqual(len(extractor.workforce.pops), len(expected_workforce))
            for (real_job, real_pop), (expected_job, expected_pop) in zip(extractor.workforce.pops.items(), expected_workforce.items()):
                self.assertEqual(real_job, expected_job)
                self.assertEqual(real_pop.job, expected_pop.job)
                self.assertAlmostEqual(real_pop.size, expected_pop.size)
            