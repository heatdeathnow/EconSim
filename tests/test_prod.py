from parameterized import parameterized
from typing import Optional
from unittest import TestCase
from source.exceptions import NegativeAmountError

from source.pop import ComFactory, Community, Jobs, Pop, Strata, PopFactory
from source.goods import Goods, Stockpile
from source.prod import ExtFactory, Extractor

class TestExtractorFactory(TestCase):

    @parameterized.expand([
        (Extractor(Goods.WHEAT, ComFactory.job(), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, None),
        (Extractor(Goods.IRON, ComFactory.job(), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.IRON, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, None),
        (Extractor(Goods.WHEAT, ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 10})),
        (Extractor(Goods.WHEAT, ComFactory.job({Jobs.FARMER: 999, Jobs.SPECIALIST: 1}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 999, Jobs.SPECIALIST: 1})),

        (Extractor(Goods.WHEAT, ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 10}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 100, Jobs.SPECIALIST: 10}),
        (Extractor(Goods.WHEAT, ComFactory.job({Jobs.FARMER: 999, Jobs.SPECIALIST: 1}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 999, Jobs.SPECIALIST: 1}),
    
        (ValueError,
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.MINER: 10})),
        (ValueError,
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.MINER: 10}),
        (ValueError,
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.NONE: 10}, None),
        (ValueError,
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 991, Jobs.SPECIALIST: 10})),

        (NegativeAmountError,
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: -10}, None),

        (TypeError,
        Jobs.FARMER, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, None),
        (TypeError,
        Goods.WHEAT, {Goods.WHEAT: 990, Jobs.SPECIALIST: 10}, None)
    ])
    def test_default(self,
                     expected: Extractor | type[Exception],
                     product: Goods,
                     needed_workers: dict[Jobs, int | float],
                     workforce: Optional[Community] = None):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, ExtFactory.default, product, needed_workers, workforce)

        else:
            extractor = ExtFactory.default(product, needed_workers, workforce)

            self.assertEqual(extractor.product, expected.product)

            self.assertEqual(len(extractor.workforce), len(expected.workforce))
            for job, pop in extractor.workforce.items():
                expected_pop = expected.workforce[job]
                self.assertEqual(expected_pop.size, pop.size)
                self.assertEqual(expected_pop.stratum, pop.stratum)
            
            self.assertEqual(len(extractor.needed_workers), len(expected.needed_workers))
            for job, size in extractor.needed_workers.items():
                self.assertEqual(expected.needed_workers[job], size)

    @parameterized.expand([
        (Extractor(Goods.WHEAT, ComFactory.job({Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        (Extractor(Goods.IRON, ComFactory.job({Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        Goods.IRON, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),

        (ValueError,
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.NONE: 10}),

        (TypeError,
        Jobs.FARMER, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        (TypeError,
        Goods.WHEAT, {Goods.WHEAT: 990, Jobs.SPECIALIST: 10})
    ])
    def test_full(self, expected: Extractor | type[Exception], product: Goods, needed_workers: dict[Jobs, int | float]):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, ExtFactory.full, product, needed_workers)

        else:
            extractor = ExtFactory.full(product, needed_workers)

            self.assertEqual(extractor.product, expected.product)

            self.assertEqual(len(extractor.workforce), len(expected.workforce))
            for job, pop in extractor.workforce.items():
                expected_pop = expected.workforce[job]
                self.assertEqual(expected_pop.size, pop.size)
                self.assertEqual(expected_pop.stratum, pop.stratum)
            
            self.assertEqual(len(extractor.needed_workers), len(expected.needed_workers))
            for job, size in extractor.needed_workers.items():
                self.assertEqual(expected.needed_workers[job], size)

class TestExtractor(TestCase):

    @parameterized.expand([
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 1000),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 500, Jobs.MINER: 500}), 1000),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 250, Jobs.MINER: 500}), 750),
    ])
    def test_capacity(self, extractor: Extractor, expected: int | float):
        self.assertAlmostEqual(extractor.capacity, expected)

    @parameterized.expand([
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 1000),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 500, Jobs.SPECIALIST: 10}), 510),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 490, Jobs.SPECIALIST: 10}), 500),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 490}), 490),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 0),
    ])
    def test_calc_total_workers(self, extractor: Extractor, expected: int | float):
        self.assertAlmostEqual(extractor.calc_total_workers(), expected)
    
    @parameterized.expand([
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 0.0),

        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 1.0),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}), 0.5),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495}), 0.25),
        
        # This needs to, and will eventually, be changed
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}), 0.5),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 5}), 0.25),
    ])
    def test_calc_efficiency(self, extractor: Extractor, expected: float):
        self.assertAlmostEqual(extractor.calc_efficiency(), expected)
    
    @parameterized.expand([
        # Current fixed throughput (will be changed in the future.): THROUGHPUT = 1.25
        # Extractor.THROUGHPUT * self.calc_total_workers() * self.calc_efficiency()

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Stockpile()),

        # 1.25 * 1000 * 1.0 = 1250
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Stockpile({Goods.WHEAT: 1250})),
        (ExtFactory.full(Goods.IRON, {Jobs.MINER: 990, Jobs.SPECIALIST: 10}), Stockpile({Goods.IRON: 1250})),

        # 1.25 * 1000 * 0.5 = 625
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 1000}),
         Stockpile({Goods.WHEAT: 625})),
        
        # 1.25 * 990 * 0.5 = 618.75
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 990}),
         Stockpile({Goods.WHEAT: 618.75})),

        # 1.25 * 10 * 0.5 = 6.25
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}),  # WILL BE CHANGED
         Stockpile({Goods.WHEAT: 6.25})),
        
        # 1.25 * 495 * 0.25 = 154.6875
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495}),
         Stockpile({Goods.WHEAT: 154.6875})),

        # 1.25 * 5 * 0.25 = 1.5625
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 5}),  # WILL BE CHANGED
         Stockpile({Goods.WHEAT: 1.5625})),

        # 1.25 * 500 * 0.5 = 312.5
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}),
         Stockpile({Goods.WHEAT: 312.5})),
        
        # 1.25 * 500 * 0.r7020 = 438.7r62
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 400, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 438.762626263})),
    ])
    def test_produce(self, extractor: Extractor, expected: Stockpile):
        stockpile = extractor.produce()

        self.assertEqual(len(stockpile), len(expected))
        for good, size in stockpile.items():
            self.assertAlmostEqual(size, expected[good])
    
    @parameterized.expand([
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), {}),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}),
         {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}),
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 990}),
         {Jobs.SPECIALIST: 10}),
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 1000}), {}),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 500}),
         {Jobs.FARMER: 500}),
    ])
    def test_calc_labor_demand(self, extractor: Extractor, expected: dict[Jobs, int | float]):
        labor_demand = extractor.calc_labor_demand()

        self.assertEqual(len(labor_demand), len(expected))
        for job, need in labor_demand.items():
            self.assertAlmostEqual(need, expected[job])

    @parameterized.expand([
        # --- NEEDS ---
        # LOWER  - 1.0 WHEAT
        # MIDDLE - 2.0 WHEAT, 1.0 IRON

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Stockpile()),

        # wheat: 990 + 20 = 1010. iron: 10
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Stockpile({Goods.WHEAT: 1010, Goods.IRON: 10})),

        # wheat: 495 + 10 = 505. iron: 5
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}),
         Stockpile({Goods.WHEAT: 505, Goods.IRON: 5})),

        # wheat: 990
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 990}),
         Stockpile({Goods.WHEAT: 990})),
        
        # wheat: 20. iron: 10
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}),
         Stockpile({Goods.WHEAT: 20, Goods.IRON: 10})),

    ])
    def test_goods_demand(self, extractor: Extractor, expected: Stockpile):
        goods_demand = extractor.calc_goods_demand()

        self.assertEqual(len(goods_demand), len(expected))
        for good, amount in goods_demand.items():
            self.assertAlmostEqual(amount, expected[good])

    @parameterized.expand([
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.FARMER, 100), True),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.MINER, 100), False),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.SPECIALIST, 100), True),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.stratum(Strata.LOWER, 100), True),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.stratum(Strata.MIDDLE, 100), True),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.stratum(Strata.UPPER, 100), False),

        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.FARMER, 100), False),
    ])
    def test_can_employ(self, extractor: Extractor, pop: Pop, expected: bool):
        self.assertEqual(extractor.can_employ(pop), expected)

    @parameterized.expand([
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.FARMER, 100),
         ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 100}), PopFactory.job(Jobs.FARMER)),
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.SPECIALIST, 100),
        ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.SPECIALIST, 90)),
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.job(Jobs.FARMER, 1000),
         ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 990}), PopFactory.job(Jobs.FARMER, 10)),
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.stratum(Strata.LOWER, 100),
         ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 100}), PopFactory.stratum(Strata.LOWER)),
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), PopFactory.stratum(Strata.MIDDLE, 100),
         ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}),
         PopFactory.stratum(Strata.MIDDLE, 90)),
    ])      
    def test_employ(self, extractor: Extractor, pop: Pop, expected_extractor: Extractor, expected_pop: Pop):
        extractor.employ(pop)

        self.assertAlmostEqual(pop.size, expected_pop.size)
        self.assertEqual(pop.stratum, expected_pop.stratum)
        self.assertEqual(pop.job, expected_pop.job)

        self.assertEqual(len(extractor.workforce), len(expected_extractor.workforce))
        for job, pop in extractor.workforce.items():
            self.assertAlmostEqual(pop.size, expected_extractor.workforce[job].size)
