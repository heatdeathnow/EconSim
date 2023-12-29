from source.pop import ComFactory, Community, Jobs, Pop, Strata, PopFactory
from source.exceptions import NegativeAmountError
from source.prod import ExtFactory, Extractor
from source.goods import Goods, Stockpile
from parameterized import parameterized
from unittest import TestCase, skip
from typing import Optional


class TestExtractorFactory(TestCase):

    @parameterized.expand([
        (Extractor(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job()),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, None),
        (Extractor(Goods.IRON, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job()),
        Goods.IRON, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, None),
        (Extractor(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 10})),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 10})),
        (Extractor(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 999, Jobs.SPECIALIST: 1})),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 999, Jobs.SPECIALIST: 1})),

        (Extractor(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 10})),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 100, Jobs.SPECIALIST: 10}),
        (Extractor(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 999, Jobs.SPECIALIST: 1})),
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
        (Extractor(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 990, Jobs.SPECIALIST: 10})),
        Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}),
        (Extractor(Goods.IRON, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, ComFactory.job({Jobs.FARMER: 990, Jobs.SPECIALIST: 10})),
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
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 900, Jobs.SPECIALIST: 100}), {Jobs.FARMER: 0.9, Jobs.SPECIALIST: 0.1}),
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 900, Jobs.SPECIALIST: 100}), {Jobs.FARMER: 0.9, Jobs.SPECIALIST: 0.1}),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 450, Jobs.MINER: 450, Jobs.SPECIALIST: 100}), 
         {Jobs.FARMER: 0.45, Jobs.MINER: 0.45, Jobs.SPECIALIST: 0.1}),
    ])
    def test_efficient_shares(self, extractor: Extractor, expected: dict[Jobs, float]):
        self.assertEqual(len(extractor.efficient_shares), len(expected))
        self.assertAlmostEqual(sum(extractor.efficient_shares.values()), 1)

        for job, share in extractor.efficient_shares.items():
            self.assertTrue(share >= 0)
            self.assertTrue(share <= 1)

            self.assertAlmostEqual(share, expected[job])

    @parameterized.expand([
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 0.0),

        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), 1.0),

        # size: 500
        # efficient_shares --- farmer: 990/1000 = .99 | specialist: 10/1000 = .01
        # shares           --- farmer: 495/500  = .99 | specialist: 5 / 500 = .01
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}), 1),

        # size: 505
        # efficient_shares    --- farmer: 990/1000       = .99      | specialist: 10/1000        = .01
        # shares              --- farmer: 495/505        = .r9801   | specialist: 10 / 505       = .r0198
        # difference          --- farmer: .99 - .r9801   = .00r9801 | specialist: .r0198 - .01   = .00r9801
        # weighted difference --- farmer: .00r9801 / .99 = .r0099   | specialist: .00r9801 / .01 = .r9801
        # efficiency          --- 1 - (.r0099 + .r9801) / 2 = .r5049
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 10}), 0.50495049),

        # size: 495
        # efficient_shares    --- farmer: 990/1000   = .99  | specialist: 10/1000   = .01
        # shares              --- farmer: 495/495    = 1    | specialist: 0 / 495   = 0
        # difference          --- farmer: 1 - 0.99   = .01  | specialist: .01 - 0   = .01
        # weighted difference --- farmer: .01 / .99  = .r01 | specialist: .01 / .01 = 1
        # efficiency          --- 1 - (.r01 + 1) / 2 = .r49
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495}), 0.49494949),
        
        # size: 10
        # efficient_shares    --- farmer: 990/1000  = .99 | specialist: 10/1000   = .01
        # shares              --- farmer: 0  /  10  = 0   | specialist: 10 / 10   = 1
        # difference          --- farmer: .99 - 0   = .99 | specialist: 1 - .01   = .99
        # weighted difference --- farmer: .99 / .99 = 1   | specialist: .99 / .01 = 1
        # efficiency          --- 1 - (1 + 1) / 2   = 0
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}), 0),

        # size: 5
        # efficient_shares    --- farmer: 990/1000  = .99 | specialist: 10/1000   = .01
        # shares              --- farmer: 0  /  5   = 0   | specialist: 5 /   5   = 1
        # difference          --- farmer: .99 - 0   = .99 | specialist: 1 - .01   = .99
        # weighted difference --- farmer: .99 / .99 = 1   | specialist: .99 / .01 = 1
        # efficiency          --- 1 - (1 + 1) / 2   = 0
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 5}), 0),
    ])
    def test_calc_efficiency(self, extractor: Extractor, expected: float):
        self.assertAlmostEqual(extractor.calc_efficiency(), expected)
    
    @parameterized.expand([
        # Current fixed throughput (will be changed in the future.): THROUGHPUT = 1.25
        # Extractor.THROUGHPUT * self.calc_total_workers() * self.calc_efficiency()

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Stockpile()),

        # THROUGHPUT * size * efficiency
        # 1.25 * 1000 * 1.0 = 1250
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Stockpile({Goods.WHEAT: 1250})),
        (ExtFactory.full(Goods.IRON, {Jobs.MINER: 990, Jobs.SPECIALIST: 10}), Stockpile({Goods.IRON: 1250})),

        # 1.25 * 1000 * 0.r49 = 618.r68
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 1000}),
         Stockpile({Goods.WHEAT: 618.68686869})),
        
        # 1.25 * 990 * 0.r49 = 612.4r9
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 990}),
         Stockpile({Goods.WHEAT: 612.49999999})),

        # 1.25 * 10 * 0 = 0
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 10}), Stockpile()),
        
        # 1.25 * 495 * 0.r49 = 306.25
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495}), Stockpile({Goods.WHEAT: 306.25})),

        # 1.25 * 5 * 0 = 0
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 5}), Stockpile()),

        # 1.25 * 500 * 1 = 625
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 495, Jobs.SPECIALIST: 5}),
         Stockpile({Goods.WHEAT: 625})),
        
        # size: 500
        # efficient_shares    --- farmer: 990/1000   = .99  | specialist: 10/1000   = .01
        # shares              --- farmer: 400/500    = .8   | specialist: 100/500   = .2
        # difference          --- farmer: .99 - .8   = .19  | specialist: .2 - .01  = .19
        # weighted difference --- farmer: .19 / .99  = .r19 | specialist: .19 / .01 = 1
        # efficiency          --- 1 - (.r19 + 1) / 2 = 0.r40
        # production          --- 1.25 * 500 * 0.r40 = 252.r52
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 400, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 252.52525253})),
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
            self.assertAlmostEqual(need.size, expected[job])  # type: ignore

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
