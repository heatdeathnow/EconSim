from source import DECIMAL_CASES
from source.pop import ComFactory, Community, Pop, Jobs, Strata, PopFactory
from source.exceptions import NegativeAmountError
from source.goods import Goods, Stockpile
from parameterized import parameterized
from typing import Literal, Optional
from unittest import TestCase


class TestPopFactory(TestCase):

    @parameterized.expand([
        (Jobs.FARMER, 100, 0.5, (100, 0.5, Strata.LOWER, Jobs.FARMER)),
        (Jobs.MINER, 100, 0.5, (100, 0.5, Strata.LOWER, Jobs.MINER)),
        (Jobs.SPECIALIST, 100, 0.5, (100, 0.5, Strata.MIDDLE, Jobs.SPECIALIST)),
        (Jobs.NONE, 100, 0.5, ValueError),

        (Jobs.FARMER, 0, 0.5, (0, Pop.ZERO_SIZE_WELFARE, Strata.LOWER, Jobs.FARMER)),
        (Jobs.FARMER, -1, 0.5, ValueError),

        (Jobs.FARMER, 100, 0, (100, 0.0, Strata.LOWER, Jobs.FARMER)),
        (Jobs.FARMER, 100, 1, (100, 1.0, Strata.LOWER, Jobs.FARMER)),
        (Jobs.FARMER, 100, -0.1, ValueError),
        (Jobs.FARMER, 100, 1.1, ValueError),

        ('farmer', 100, 0.5, TypeError),
        (Jobs.FARMER, '100', 0.5, TypeError),
        (Jobs.FARMER, 100, '0.5', TypeError),
    ])
    def test_job(self, job: Jobs, size: int | float, welfare: int | float,
                                                 #    size,      welfare,   stratum, job
                 expected: type[Exception] | tuple[int | float, int | float, Strata, Jobs]):

        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                PopFactory.job(job, size, welfare)
        
        else:
            pop = PopFactory.job(job, size, welfare)

            self.assertAlmostEqual(pop.size, expected[0])
            self.assertAlmostEqual(pop.welfare, expected[1])
            self.assertEqual(pop.stratum, expected[2])
            self.assertEqual(pop.job, expected[3])

    @parameterized.expand([
        (Strata.LOWER, 100, 0.5, (100, 0.5, Strata.LOWER, Jobs.NONE)),
        (Strata.MIDDLE, 100, 0.5, (100, 0.5, Strata.MIDDLE, Jobs.NONE)),
        (Strata.UPPER, 100, 0.5, (100, 0.5, Strata.UPPER, Jobs.NONE)),

        (Strata.LOWER, -100, 0.5, ValueError),
        (Strata.LOWER, 100, -0.5, ValueError),
        (Strata.LOWER, 100, 1.5, ValueError),

        ('lower', 100, 1.5, TypeError),
        (Strata.LOWER, '100', 1.5, TypeError),
        (Strata.LOWER, 100, '1.5', TypeError),
    ])
    def test_stratum(self, stratum: Strata, size: int | float, welfare: int | float,
                     expected: type[Exception] | tuple[int | float, int | float, Strata, Jobs]):
        
        if isinstance(expected, type) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                PopFactory.stratum(stratum, size, welfare)
        
        else:
            pop = PopFactory.stratum(stratum, size, welfare)

            self.assertAlmostEqual(pop.size, expected[0])
            self.assertAlmostEqual(pop.welfare, expected[1])
            self.assertEqual(pop.stratum, expected[2])
            self.assertEqual(pop.job, expected[3])

class TestPop(TestCase):

    def setUp(self):
        self.test_farmer = PopFactory.job(Jobs.FARMER, 100, 0.5)
    
    def tearDown(self):
        del self.test_farmer
    
    @parameterized.expand([
        (PopFactory.job(Jobs.FARMER, 100, 0.5), PopFactory.job(Jobs.FARMER, 200, 0.5)),
        (PopFactory.job(Jobs.FARMER, 100, 1), PopFactory.job(Jobs.FARMER, 200, 0.75)),
        (PopFactory.job(Jobs.FARMER, 50, 0.5), PopFactory.job(Jobs.FARMER, 150, 0.5)),
        (PopFactory.job(Jobs.FARMER, 100, 0), PopFactory.job(Jobs.FARMER, 200, 0.25)),

        (PopFactory.job(Jobs.FARMER, 50, 0), PopFactory.job(Jobs.FARMER, 150, 1/3)),
        (PopFactory.job(Jobs.FARMER, 50, 1), PopFactory.job(Jobs.FARMER, 150, 2/3)),
        (PopFactory.job(Jobs.FARMER, 200, 0), PopFactory.job(Jobs.FARMER, 300, 1/6)),
        (PopFactory.job(Jobs.FARMER, 200, 1), PopFactory.job(Jobs.FARMER, 300, 5/6)),

        (PopFactory.job(Jobs.MINER, 100), ValueError),
        (PopFactory.stratum(Strata.MIDDLE, 100), ValueError),
        ('test', TypeError),
    ])
    def test_add(self, pop: Pop, expected: type[Exception] | Pop):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, self.test_farmer.__add__, pop)
            self.assertRaises(expected, self.test_farmer.__iadd__, pop)

        else:

            new_pop = self.test_farmer + pop
            self.test_farmer += pop
 
            for pop in (new_pop, self.test_farmer):
                self.assertEqual(pop.stratum, expected.stratum)
                self.assertEqual(pop.job, expected.job)
                self.assertAlmostEqual(pop.size, expected.size)
                self.assertAlmostEqual(pop.welfare, expected.welfare)

    @parameterized.expand([
        (PopFactory.job(Jobs.FARMER, 50, 0.5), PopFactory.job(Jobs.FARMER, 50, 0.5)),
        (PopFactory.job(Jobs.FARMER, 25, 0.5), PopFactory.job(Jobs.FARMER, 75, 0.5)),
        (PopFactory.job(Jobs.FARMER, 75, 0.5), PopFactory.job(Jobs.FARMER, 25, 0.5)),
        (PopFactory.job(Jobs.FARMER, 100, 0.5), PopFactory.job(Jobs.FARMER, 0, 0.5)),

        (PopFactory.job(Jobs.FARMER, 50, 0.25), PopFactory.job(Jobs.FARMER, 50, 0.75)),
        (PopFactory.job(Jobs.FARMER, 50, 0.75), PopFactory.job(Jobs.FARMER, 50, 0.25)),
        (PopFactory.job(Jobs.FARMER, 50, 1), PopFactory.job(Jobs.FARMER, 50, 0)),
        
        (PopFactory.job(Jobs.FARMER, 51, 1), NegativeAmountError),
        (PopFactory.job(Jobs.FARMER, 101, 0), NegativeAmountError),
        (PopFactory.job(Jobs.MINER, 50), ValueError),
        (PopFactory.stratum(Strata.MIDDLE, 50), ValueError),
        ('test', TypeError),
    ])
    def test_sub(self, pop: Pop, expected: type[Exception] | Pop):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, self.test_farmer.__sub__, pop)
            self.assertRaises(expected, self.test_farmer.__isub__, pop)

        else:
            new_pop = self.test_farmer - pop
            self.test_farmer -= pop

            for pop in (new_pop, self.test_farmer):
                self.assertEqual(pop.stratum, expected.stratum)
                self.assertEqual(pop.job, expected.job)
                self.assertAlmostEqual(pop.size, expected.size)
                self.assertAlmostEqual(pop.welfare, expected.welfare)

    @parameterized.expand([
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.FARMER, 90), True, True, False, False, False),
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.MINER, 90), True, True, False, False, False),
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.stratum(Strata.LOWER, 90), True, True, False, False, False),

        (PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.FARMER, 100), False, True, False, True, True),
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.MINER, 100), False, True, False, True, True),
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.stratum(Strata.LOWER, 100), False, True, False, True, True),

        (PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.FARMER, 110), False, False, True, True, False),
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.job(Jobs.MINER, 110), False, False, True, True, False),
        (PopFactory.job(Jobs.FARMER, 100), PopFactory.stratum(Strata.LOWER, 110), False, False, True, True, False),
    ])
    def test_comparisons(self, pop1: Pop, pop2: Pop, gt: bool, ge: bool, lt: bool, le: bool, eq: bool):
        self.assertEqual(pop1 > pop2, gt)
        self.assertEqual(pop1 >= pop2, ge)
        self.assertEqual(pop1 < pop2, lt)
        self.assertEqual(pop1 <= pop2, le)
        self.assertEqual(pop1 == pop2, eq)

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (PopFactory.job(Jobs.FARMER, 100), Stockpile({Goods.WHEAT: 100 * Strata.LOWER.needs[Goods.WHEAT]})),
        (PopFactory.job(Jobs.MINER, 100), Stockpile({Goods.WHEAT: 100* Strata.LOWER.needs[Goods.WHEAT]})),
        (PopFactory.job(Jobs.SPECIALIST, 100), Stockpile({Goods.WHEAT: 100 * Strata.MIDDLE.needs[Goods.WHEAT],
                                                          Goods.IRON: 100 * Strata.MIDDLE.needs[Goods.IRON]})),

        (PopFactory.job(Jobs.FARMER, 50.55), Stockpile({Goods.WHEAT: 50.55 * Strata.LOWER.needs[Goods.WHEAT]})),
        (PopFactory.job(Jobs.SPECIALIST, 50.55), Stockpile({Goods.WHEAT: 50.55 * Strata.MIDDLE.needs[Goods.WHEAT],
                                                            Goods.IRON: 50.55 * Strata.MIDDLE.needs[Goods.IRON]})),
    ])
    def test_consumption(self, pop: Pop, expected: Stockpile):

        consumption = pop.calc_consumption()

        self.assertEqual(len(consumption), len(expected))

        for (real_good, real_amount), (expected_good, expected_amount) in zip(consumption.items(), expected.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (PopFactory.job(Jobs.FARMER, 100, 0.5), Stockpile({Goods.WHEAT: 100}), 5/6),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
        (PopFactory.job(Jobs.FARMER, 100, 0.5), Stockpile({Goods.WHEAT: 50}), 0.5),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
        (PopFactory.job(Jobs.FARMER, 100, 0.5), Stockpile(), 1/6),  # 1/3 * 0.5 + 2/3 * 0 = 1/6

        (PopFactory.job(Jobs.SPECIALIST, 100, 0.5), Stockpile({Goods.WHEAT: 200, Goods.IRON: 100}), 5/6),
        (PopFactory.job(Jobs.SPECIALIST, 100, 0.5), Stockpile({Goods.WHEAT: 200}), 0.5),
        (PopFactory.job(Jobs.SPECIALIST, 100, 0.5), Stockpile({Goods.IRON: 100}), 0.5),
        # 1/3 * 0.5 + 2/3 * 0.58r3 = 0.r5
        (PopFactory.job(Jobs.SPECIALIST, 100, 0.5), Stockpile({Goods.WHEAT: 100, Goods.IRON: 50}), 0.55555555),
        (PopFactory.job(Jobs.SPECIALIST, 100, 0.5), Stockpile(), 1/6),

        (PopFactory.job(Jobs.FARMER, 0, 0.5), Stockpile(), 0.0),
        (PopFactory.job(Jobs.FARMER, 0, 0.5), Stockpile({Goods.WHEAT: 100}), 0.0),
    ])
    def test_welfare(self, pop: Pop, stockpile: Stockpile, expected: float):
        pop.update_welfare(pop.calc_consumption(), stockpile)
        self.assertAlmostEqual(pop.welfare, expected, DECIMAL_CASES)

    @parameterized.expand([
        # WELFARE_THRESHOLD = 0.51
        # GROWTH_RATE = 0.05

        (PopFactory.job(Jobs.FARMER, 100, 1), PopFactory.job(Jobs.FARMER, 105, 1)),
        (PopFactory.job(Jobs.FARMER, 100, 0.51), PopFactory.job(Jobs.FARMER, 105, 0.51)),
        (PopFactory.job(Jobs.FARMER, 100, 0.5), PopFactory.job(Jobs.FARMER, 95, 0.50)),
        (PopFactory.job(Jobs.FARMER, 100, 0.49), PopFactory.job(Jobs.FARMER, 95, 0.49)),
        (PopFactory.job(Jobs.FARMER, 100, 0), PopFactory.job(Jobs.FARMER, 95, 0)),
    ])
    def test_resize(self, pop: Pop, expected: Pop):
        pop.resize()
        self.assertAlmostEqual(pop.size, expected.size)

    @parameterized.expand([
        (PopFactory.job(Jobs.FARMER, 100, 1), True),
        (PopFactory.job(Jobs.FARMER, 100, 0.51), True),
        (PopFactory.job(Jobs.FARMER, 100, 0.5), False),
        (PopFactory.job(Jobs.FARMER, 100, 0.49), False),
        (PopFactory.job(Jobs.FARMER, 100, 0), False),

        (PopFactory.stratum(Strata.MIDDLE, 100, 1), False),
        (PopFactory.stratum(Strata.MIDDLE, 100, 0.51), False),
        (PopFactory.stratum(Strata.MIDDLE, 100, 0.5), False),
        (PopFactory.stratum(Strata.MIDDLE, 100, 0.49), False),
        (PopFactory.stratum(Strata.MIDDLE, 100, 0), False),
    ])
    def test_can_promote(self, pop: Pop, expected: bool):
        self.assertEqual(pop.can_promote(), expected)

    @parameterized.expand([
    # WELFARE_THRESHOLD = 0.51
    # PROMOTE_RATE = 0.01

    (PopFactory.job(Jobs.FARMER, 100, 0.51), PopFactory.stratum(Strata.MIDDLE, 1, 0.51)),
    (PopFactory.job(Jobs.MINER, 100, 0.51), PopFactory.stratum(Strata.MIDDLE, 1, 0.51)),
    (PopFactory.stratum(Strata.LOWER, 100, 0.51), PopFactory.stratum(Strata.MIDDLE, 1, 0.51)),
    ])
    def test_promote(self, pop: Pop, expected: Pop):
        promoted = pop.promote()

        self.assertEqual(promoted.job, expected.job)
        self.assertEqual(promoted.stratum, expected.stratum)
        self.assertAlmostEqual(promoted.size, expected.size)
        self.assertAlmostEqual(promoted.welfare, expected.welfare)

class TestComFactory(TestCase):

    @parameterized.expand([
        ({Jobs.FARMER: 90, Jobs.SPECIALIST: 10},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 90), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 10)}),
        
        ({Jobs.FARMER: 90, Jobs.SPECIALIST: 0},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 90)}),
        ({}, {}),
        (None, {}),
        
        ('test', TypeError),
        ({Jobs.FARMER: 90, Jobs.NONE: 10}, ValueError),
        ({Strata.LOWER: 90, Strata.MIDDLE: 10}, TypeError),
    ])
    def test_job(self, want: Optional[dict[Jobs, int | float]], expected: type[Exception] | dict[Jobs, Pop]):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, ComFactory.job, want)
        
        else:
            community = ComFactory.job(want)

            self.assertEqual(len(expected), len(community))
            for expected_key, expected_pop in expected.items():
                self.assertEqual(community[expected_key].stratum, expected_pop.stratum)
                self.assertEqual(community[expected_key].job, expected_pop.job)
                self.assertAlmostEqual(community[expected_key].size, expected_pop.size)
                self.assertAlmostEqual(community[expected_key].welfare, expected_pop.welfare)

    @parameterized.expand([
        ({Jobs.FARMER: (90, 0.5), Jobs.SPECIALIST: (10, 0.5)},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 90, 0.5), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 10, 0.5)}),
        
        ({Jobs.FARMER: (90, 1), Jobs.SPECIALIST: (10, 0)},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 90, 1), Jobs.SPECIALIST: PopFactory.job(Jobs.SPECIALIST, 10, 0)}),
        
        ({Jobs.FARMER: (90, 0.45), Jobs.SPECIALIST: 0},
         {Jobs.FARMER: PopFactory.job(Jobs.FARMER, 90, 0.45)}),
        ({}, {}),
        (None, {}),
        
        ('test', TypeError),
        ({Jobs.FARMER: 90, Jobs.NONE: 10}, ValueError),
        ({Strata.LOWER: 90, Strata.MIDDLE: 10}, TypeError),
    ])
    def test_job_welfare(self, want: Optional[dict[Jobs, tuple[int | float, int | float]]], expected: type[Exception] | dict[Jobs, Pop]):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, ComFactory.job_welfare, want)
        
        else:
            community = ComFactory.job_welfare(want)

            self.assertEqual(len(expected), len(community))
            for expected_key, expected_pop in expected.items():
                self.assertEqual(community[expected_key].stratum, expected_pop.stratum)
                self.assertEqual(community[expected_key].job, expected_pop.job)
                self.assertAlmostEqual(community[expected_key].size, expected_pop.size)
                self.assertAlmostEqual(community[expected_key].welfare, expected_pop.welfare)

    @parameterized.expand([
        ({Strata.LOWER: 90, Strata.MIDDLE: 10},
         {Strata.LOWER: PopFactory.stratum(Strata.LOWER, 90), Strata.MIDDLE: PopFactory.stratum(Strata.MIDDLE, 10)}),
        
        ({Strata.LOWER: 90, Strata.MIDDLE: 0},
         {Strata.LOWER: PopFactory.stratum(Strata.LOWER, 90)}),
        ({}, {}),
        (None, {}),
        
        ('test', TypeError),
        ({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, TypeError),
    ])
    def test_stratum(self, want: Optional[dict[Strata, int | float]], expected: type[Exception] | dict[Strata, Pop]):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, ComFactory.stratum, want)
        
        else:
            community = ComFactory.stratum(want)

            self.assertEqual(len(expected), len(community))
            for expected_key, expected_pop in expected.items():
                self.assertEqual(community[expected_key, Jobs.NONE].stratum, expected_pop.stratum)
                self.assertEqual(community[expected_key, Jobs.NONE].job, Jobs.NONE)
                self.assertAlmostEqual(community[expected_key, Jobs.NONE].size, expected_pop.size)
                self.assertAlmostEqual(community[expected_key, Jobs.NONE].welfare, expected_pop.welfare)

    @parameterized.expand([
        ({Strata.LOWER: (90, 0.5), Strata.MIDDLE: (10, 0.5)},
         {Strata.LOWER: PopFactory.stratum(Strata.LOWER, 90, 0.5), Strata.MIDDLE: PopFactory.stratum(Strata.MIDDLE, 10, 0.5)}),
        
        ({Strata.LOWER: (90, 1), Strata.MIDDLE: (10, 0)},
         {Strata.LOWER: PopFactory.stratum(Strata.LOWER, 90, 1), Strata.MIDDLE: PopFactory.stratum(Strata.MIDDLE, 10, 0)}),
        
        ({Strata.LOWER: (90, 0.45), Strata.MIDDLE: 0},
         {Strata.LOWER: PopFactory.stratum(Strata.LOWER, 90, 0.45)}),
        ({}, {}),
        (None, {}),
        
        ('test', TypeError),
        ({Strata.LOWER: 90, Jobs.SPECIALIST: 10}, TypeError),
    ])
    def test_stratum_welfare(self, want: Optional[dict[Strata, tuple[int | float, int | float]]], expected: type[Exception] | dict[Strata, Pop]):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, ComFactory.stratum_welfare, want)
        
        else:
            community = ComFactory.stratum_welfare(want)

            self.assertEqual(len(expected), len(community))
            for expected_key, expected_pop in expected.items():
                self.assertEqual(community[expected_key, Jobs.NONE].stratum, expected_pop.stratum)
                self.assertEqual(community[expected_key, Jobs.NONE].job, Jobs.NONE)
                self.assertAlmostEqual(community[expected_key, Jobs.NONE].size, expected_pop.size)
                self.assertAlmostEqual(community[expected_key, Jobs.NONE].welfare, expected_pop.welfare)

class TestCommunity(TestCase):

    def setUp(self) -> None:
        self.community = ComFactory.job({Jobs.FARMER: 100})
    
    def tearDown(self) -> None:
        del self.community
    
    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100}), ComFactory.job({Jobs.FARMER: 200})),
        (ComFactory.job({Jobs.MINER: 100}), ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100})),
        (ComFactory.job(), ComFactory.job({Jobs.FARMER: 100})),

        (PopFactory.job(Jobs.FARMER, 100), ComFactory.job({Jobs.FARMER: 200})),
        (PopFactory.job(Jobs.MINER, 100), ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100})),

        (PopFactory.stratum(Strata.LOWER, 100), Community([PopFactory.job(Jobs.FARMER, 100), PopFactory.stratum(Strata.LOWER, 100)])),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 100}),
         Community([PopFactory.job(Jobs.FARMER, 100), PopFactory.stratum(Strata.LOWER, 100), PopFactory.stratum(Strata.MIDDLE, 100)])),

        ('test', TypeError),
    ])
    def test_add(self, community: Community | Pop, expected: type[Exception] | Community):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, self.community.__add__, community)
            self.assertRaises(expected, self.community.__iadd__, community)
        
        else:

            new = self.community + community
            self.community += community

            self.assertEqual(len(new), len(self.community))
            self.assertEqual(len(new), len(expected))

            for key, val in expected.items():
                self.assertEqual(val.stratum, new[key].stratum)
                self.assertEqual(val.stratum, self.community[key].stratum)

                self.assertEqual(val.job, new[key].job)
                self.assertEqual(val.job, self.community[key].job)

                self.assertAlmostEqual(val.size, new[key].size)
                self.assertAlmostEqual(val.size, self.community[key].size)

                self.assertAlmostEqual(val.welfare, new[key].welfare)
                self.assertAlmostEqual(val.welfare, self.community[key].welfare)

    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 50}), ComFactory.job({Jobs.FARMER: 50})),
        (ComFactory.job({Jobs.FARMER: 100}), ComFactory.job()),
        (ComFactory.job(), ComFactory.job({Jobs.FARMER: 100})),
        (PopFactory.job(Jobs.FARMER, 50, 1), ComFactory.job_welfare({Jobs.FARMER: (50, 0)})),

        (ComFactory.job({Jobs.MINER: 100}), NegativeAmountError),
        (PopFactory.job(Jobs.MINER, 100), NegativeAmountError),
        (PopFactory.job(Jobs.FARMER, 101), NegativeAmountError),
        (PopFactory.job(Jobs.FARMER, 51, 1), NegativeAmountError),
        (PopFactory.stratum(Strata.LOWER, 100), NegativeAmountError),
        (ComFactory.job({Jobs.FARMER: 50, Jobs.MINER: 50}), NegativeAmountError),
        ('test', TypeError),
    ])
    def test_sub(self, community: Community | Pop, expected: type[Exception] | Community):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, self.community.__sub__, community)
            self.assertRaises(expected, self.community.__isub__, community)
        
        else:

            new = self.community - community
            self.community -= community

            self.assertEqual(len(new), len(self.community))
            self.assertEqual(len(new), len(expected))

            for key, val in expected.items():
                self.assertEqual(val.stratum, new[key].stratum)
                self.assertEqual(val.stratum, self.community[key].stratum)

                self.assertEqual(val.job, new[key].job)
                self.assertEqual(val.job, self.community[key].job)

                self.assertAlmostEqual(val.size, new[key].size)
                self.assertAlmostEqual(val.size, self.community[key].size)

                self.assertAlmostEqual(val.welfare, new[key].welfare)
                self.assertAlmostEqual(val.welfare, self.community[key].welfare)

    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 10}), 210),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}), 200),
        (ComFactory.job({Jobs.FARMER: 100}), 100),

        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 100, Strata.UPPER: 10}), 210),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 100}), 200),
        (ComFactory.stratum({Strata.LOWER: 100}), 100),

        (ComFactory.job({Jobs.FARMER: 100}) + ComFactory.stratum({Strata.LOWER: 100}), 200)
    ])
    def test_size(self, community: Community, expected_size: int | float):
        self.assertAlmostEqual(community.size, expected_size)
    
    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), Jobs.FARMER, 1/3),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), Jobs.MINER, 1/3),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), Jobs.SPECIALIST, 1/3),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), Strata.LOWER, 2/3),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), Strata.MIDDLE, 1/3),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), (Strata.LOWER, Jobs.NONE), 0),

        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), Strata.LOWER, 100/175),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), Strata.MIDDLE, 50/175),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), Strata.UPPER, 25/175),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), Jobs.FARMER, 0),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), (Strata.LOWER, Jobs.NONE), 100/175),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), (Strata.MIDDLE, Jobs.NONE), 50/175),
        (ComFactory.stratum({Strata.LOWER: 100, Strata.MIDDLE: 50, Strata.UPPER: 25}), (Strata.UPPER, Jobs.NONE), 25/175),
    ])
    def test_get_share_of(self, community: Community, job: Jobs | tuple[Strata, Literal[Jobs.NONE]] | Strata, expected_share: float):
        self.assertAlmostEqual(community.get_share_of(job), expected_share)
    
    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 90, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.SPECIALIST, 80)),
        (ComFactory.job({Jobs.FARMER: 79, Jobs.MINER: 90, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.FARMER, 79)),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 79, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.MINER, 79)),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 80, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.MINER, 80)),
    ])
    def test_min(self, community: Community, expected_pop: Pop):
        pop = min(community.values())

        self.assertEqual(pop.job, expected_pop.job)
        self.assertEqual(pop.stratum, expected_pop.stratum)
        self.assertAlmostEqual(pop.size, expected_pop.size)
        self.assertAlmostEqual(pop.welfare, expected_pop.welfare)

    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 90, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.FARMER, 100)),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 90, Jobs.SPECIALIST: 101}), PopFactory.job(Jobs.SPECIALIST, 101)),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 101, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.MINER, 101)),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 80}), PopFactory.job(Jobs.FARMER, 100)),
    ])
    def test_max(self, community: Community, expected_pop: Pop):
        pop = max(community.values())

        self.assertEqual(pop.job, expected_pop.job)
        self.assertEqual(pop.stratum, expected_pop.stratum)
        self.assertAlmostEqual(pop.size, expected_pop.size)
        self.assertAlmostEqual(pop.welfare, expected_pop.welfare)

    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100}), Stockpile({Goods.WHEAT: 100 * Strata.LOWER.needs[Goods.WHEAT]})),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}), Stockpile({Goods.WHEAT: 200 * Strata.LOWER.needs[Goods.WHEAT]})),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 50}), Stockpile({Goods.WHEAT: 150 * Strata.LOWER.needs[Goods.WHEAT]})),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}), 
         Stockpile({Goods.WHEAT: 100 * Strata.LOWER.needs[Goods.WHEAT] + 100 * Strata.MIDDLE.needs[Goods.WHEAT],
                    Goods.IRON: 100 * Strata.MIDDLE.needs[Goods.IRON]})),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 50}), 
         Stockpile({Goods.WHEAT: 100 * Strata.LOWER.needs[Goods.WHEAT] + 50 * Strata.MIDDLE.needs[Goods.WHEAT],
                    Goods.IRON: 50 * Strata.MIDDLE.needs[Goods.IRON]})),
    ])
    def test_calc_goods_demand(self, community: Community, expected: Stockpile):
        goods_demand = community.calc_goods_demand()

        self.assertEqual(len(goods_demand), len(expected))
        for good, amount in expected.items():
            self.assertAlmostEqual(goods_demand[good], amount)

    def test_update_welfares(self):
        """ These tests have already been written in `test_utils` """

    @parameterized.expand([

        # WELFARE_THRESHOLD = 0.51
        # GROWTH_RATE = 0.05
        # PROMOTE_RATE = 0.01

        (
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.MINER: (100, 0.5), Jobs.SPECIALIST: (100, 0.5)}),
            ComFactory.job_welfare({Jobs.FARMER: (95, 0.5), Jobs.MINER: (95, 0.5), Jobs.SPECIALIST: (95, 0.5)}),
        ),

        (
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.52), Jobs.MINER: (100, 0.52), Jobs.SPECIALIST: (100, 0.52)}),
            ComFactory.job_welfare({Jobs.FARMER: (105, 0.52), Jobs.MINER: (105, 0.52), Jobs.SPECIALIST: (105, 0.52)}),
        ),

        (
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.52), Jobs.MINER: (100, 0.50), Jobs.SPECIALIST: (100, 0)}),
            ComFactory.job_welfare({Jobs.FARMER: (105, 0.52), Jobs.MINER: (95, 0.50), Jobs.SPECIALIST: (95, 0)}),
        ),
    ])
    def test_resize_all(self, community: Community, expected: Community):
        community.resize_all()

        self.assertEqual(len(community), len(expected))
        for job, pop in expected.items():
            self.assertAlmostEqual(community[job].size, pop.size)
    
    @parameterized.expand([

        # PROMOTE_RATE = 0.01

        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 0.52)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (10, 0.52)})
        ),
        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 0.52), Jobs.MINER: (1000, 0.52)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (20, 0.52)})
        ),
        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 1), Jobs.MINER: (1000, 0.52)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (20, 0.76)})
        ),
        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 1), Jobs.MINER: (1000, 0.0)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (10, 1)})
        ),

        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 0.52), Jobs.MINER: (1000, 0.52), Jobs.SPECIALIST: (1000, 0.52)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (20, 0.52)})
        ),
        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 1), Jobs.MINER: (1000, 0.52), Jobs.SPECIALIST: (1000, 0.52)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (20, 0.76)})
        ),
        (
            ComFactory.job_welfare({Jobs.FARMER: (1000, 1), Jobs.MINER: (1000, 0), Jobs.SPECIALIST: (1000, 0.52)}),
            ComFactory.stratum_welfare({Strata.MIDDLE: (10, 1)})
        ),
    ])
    def test_promote_all(self, community: Community, expected: Community):
        promoted = community.promote_all()

        self.assertEqual(len(promoted), len(expected))

        for job, pop in expected.items():
            self.assertEqual(promoted[job].stratum, pop.stratum)
            self.assertEqual(promoted[job].job, pop.job)
            self.assertAlmostEqual(promoted[job].size, pop.size)
            self.assertAlmostEqual(promoted[job].welfare, pop.welfare)
    
    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100}), ComFactory.stratum({Strata.LOWER: 100})),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}), ComFactory.stratum({Strata.LOWER: 200})),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100, Jobs.SPECIALIST: 100}), 
         ComFactory.stratum({Strata.LOWER: 200, Strata.MIDDLE: 100})),
    ])
    def test_unemploy_all(self, community: Community, expected: Community):
        community.unemploy_all()

        for key, pop in community.items():
            self.assertEqual(pop.job, expected[key].job)
            self.assertAlmostEqual(pop.size, expected[key].size)
            self.assertAlmostEqual(pop.welfare, expected[key].welfare)

    @parameterized.expand([
        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 50}), Strata.LOWER, ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 50})),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 50}), Strata.MIDDLE, ComFactory.job({Jobs.SPECIALIST: 50})),
        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 50}), Strata.LOWER, ComFactory.job({Jobs.FARMER: 100})),
        
        (ComFactory.job_welfare({Jobs.FARMER: (100, 0.3), Jobs.SPECIALIST: (50, 0.2)}), Strata.MIDDLE, 
         ComFactory.job_welfare({Jobs.SPECIALIST: (50, 0.2)})),
    ])
    def test_filter(self, community: Community, filter: Strata, expected: Community):
        filtered = community[filter]

        self.assertEqual(len(filtered), len(expected))
        for job, pop in filtered.items():
            self.assertAlmostEqual(pop.size, expected[job].size)
            self.assertAlmostEqual(pop.welfare, expected[job].welfare)
            self.assertIs(pop, community[job])
