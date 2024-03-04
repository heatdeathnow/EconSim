from decimal import Decimal, InvalidOperation, getcontext
from typing import Literal, Optional
from unittest import skip
from source.pop import CommuneFactory, Commune, Pop, Jobs, Strata, PopFactory
from source.exceptions import NegativeAmountError
from source.goods import Products, Stock, create_stock, stock_factory
from parameterized import parameterized
from tests import GoodsMixIn, PopMixIn
D = getcontext().create_decimal

FARMER = Jobs.FARMER
MINER = Jobs.MINER
SPECIALIST = Jobs.SPECIALIST
UNEMPLOYED = Jobs.UNEMPLOYED

LOWER = Strata.LOWER
MIDDLE = Strata.MIDDLE
UPPER = Strata.UPPER

WHEAT = Products.WHEAT
IRON = Products.IRON
FLOUR = Products.FLOUR

farmer_fac = PopFactory(FARMER)
miner_fac = PopFactory(MINER)
specialist_fac = PopFactory(SPECIALIST)

lower_fac = PopFactory(LOWER)
middle_fac = PopFactory(MIDDLE)

wheat_fac = stock_factory(WHEAT)
iron_fac = stock_factory(IRON)
wheat_iron_fac = stock_factory(WHEAT, IRON)

c_farmer_fac = CommuneFactory(FARMER)
c_miner_fac = CommuneFactory(MINER)
c_farmer_miner_fac = CommuneFactory(FARMER, MINER)
c_farmer_miner_specialist = CommuneFactory(FARMER, MINER, SPECIALIST)
c_lower_middle_fac = CommuneFactory(LOWER, MIDDLE)
c_lower_middle_upper_fac = CommuneFactory(LOWER, MIDDLE, UPPER)

class TestPopFactory(PopMixIn):

    @parameterized.expand([
        (FARMER, 100, 0.5, Pop(D(100), D(0.5), LOWER, FARMER)),
        (MINER, 100, 0.5, Pop(D(100), D(0.5), LOWER, MINER)),
        (SPECIALIST, 100, 0.5, Pop(D(100), D(0.5), MIDDLE, SPECIALIST)),
        (UNEMPLOYED, 100, 0.5, ValueError),

        (FARMER, 0, 0.5, Pop(D(0), Pop.ZERO_SIZE_WELFARE, LOWER, FARMER)),
        (FARMER, -1, 0.5, NegativeAmountError),

        (FARMER, 100, 0, Pop(D(100), D(0), LOWER, FARMER)),
        (FARMER, 100, 1, Pop(D(100), D(1), LOWER, FARMER)),
        (FARMER, 100, -0.1, ValueError),
        (FARMER, 100, 1.1, ValueError),

        ('farmer', 100, 0.5, TypeError),
        (FARMER, 'test', 0.5, InvalidOperation),
    ])
    def test_job_makepop(self, job: Jobs, size: float, welfare: float, expected: type[Exception] | Pop):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, PopFactory.job_makepop, job, size, welfare)
        
        else:
            pop = PopFactory.job_makepop(job, size, welfare)
            self.assert_pops_equal(pop, expected)

    @parameterized.expand([
        (LOWER, 100, 0.5, Pop(D(100), D(0.5), LOWER, UNEMPLOYED)),
        (MIDDLE, 100, 0.5, Pop(D(100), D(0.5), MIDDLE, UNEMPLOYED)),
        (UPPER, 100, 0.5, Pop(D(100), D(0.5), UPPER, UNEMPLOYED)),

        (LOWER, -100, 0.5, NegativeAmountError),
        (LOWER, 100, -0.5, ValueError),
        (LOWER, 100, 1.5, ValueError),

        ('lower', 100, 1.5, TypeError),
        (LOWER, 'test', 1.5, InvalidOperation),
    ])
    def test_stratum_makepop(self, stratum: Strata, size: float, welfare: float, expected: type[Exception] | Pop):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, PopFactory.stratum_makepop, stratum, size, welfare)
        
        else:
            pop = PopFactory.stratum_makepop(stratum, size, welfare)
            self.assert_pops_equal(pop, expected)

class TestPop(PopMixIn, GoodsMixIn):

    @parameterized.expand([
        (farmer_fac(100), farmer_fac(100), farmer_fac(200)),
        (farmer_fac(100, 1), farmer_fac(100), farmer_fac(200, 0.75)),
        (farmer_fac(50), farmer_fac(100), farmer_fac(150)),
        (farmer_fac(100, 0), farmer_fac(100), farmer_fac(200, 0.25)),

        (farmer_fac(50, 0), farmer_fac(100), farmer_fac(150, 1/3)),
        (farmer_fac(50, 1), farmer_fac(100), farmer_fac(150, 2/3)),
        (farmer_fac(200, 0), farmer_fac(100), farmer_fac(300, 1/6)),
        (farmer_fac(200, 1), farmer_fac(100), farmer_fac(300, 5/6)),

        (miner_fac(100), miner_fac(100), miner_fac(200)),
        (lower_fac(100), lower_fac(50), lower_fac(150)),
        (middle_fac(100), middle_fac(150), middle_fac(250)),

        (miner_fac(100), farmer_fac(100), ValueError),
        (middle_fac(100), lower_fac(100), ValueError),
        (middle_fac(100), farmer_fac(100), ValueError),
        (farmer_fac(100), lower_fac(100), ValueError),
        (farmer_fac(100), 'test', TypeError),
    ])
    def test_add(self, pop1: Pop, pop2: Pop, expected: type[Exception] | Pop):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, pop1.__add__, pop2)

        else:
            new_pop = pop1 + pop2
            pop1 += pop2
            self.assert_pops_equal(new_pop, expected)
            self.assert_pops_equal(pop1, expected)

    @parameterized.expand([
        (farmer_fac(100), farmer_fac(50), farmer_fac(50)),
        (farmer_fac(100), farmer_fac(25), farmer_fac(75)),
        (farmer_fac(100), farmer_fac(75), farmer_fac(25)),
        (farmer_fac(100), farmer_fac(100), farmer_fac()),

        (farmer_fac(100), farmer_fac(50, 0.25), farmer_fac(50, 0.75)),
        (farmer_fac(100), farmer_fac(50, 0.75), farmer_fac(50, 0.25)),
        (farmer_fac(100), farmer_fac(50, 1), farmer_fac(50, 0)),
        (lower_fac(100), lower_fac(50), lower_fac(50)),
        
        (farmer_fac(100), farmer_fac(51, 1), NegativeAmountError),
        (farmer_fac(100), farmer_fac(101, 0), NegativeAmountError),
        (farmer_fac(100), miner_fac(50), ValueError),
        (farmer_fac(100), middle_fac(50), ValueError),
        (farmer_fac(100), lower_fac(50), ValueError),
        (farmer_fac(100), 'test', TypeError),
    ])
    def test_sub(self, pop1: Pop, pop2: Pop, expected: type[Exception] | Pop):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, pop1.__sub__, pop2)

        else:
            new_pop = pop1 - pop2
            pop1 -= pop2

            self.assert_pops_equal(new_pop, expected)
            self.assert_pops_equal(pop1, expected)

    @parameterized.expand([
        (farmer_fac(100), farmer_fac(90), True, True, False, False, False),
        (farmer_fac(100), miner_fac(90), True, True, False, False, False),
        (farmer_fac(100), lower_fac(90), True, True, False, False, False),

        (farmer_fac(100), farmer_fac(100), False, True, False, True, True),
        (farmer_fac(100), miner_fac(100), False, True, False, True, True),
        (farmer_fac(100), lower_fac(100), False, True, False, True, True),

        (farmer_fac(100), farmer_fac(110), False, False, True, True, False),
        (farmer_fac(100), miner_fac(110), False, False, True, True, False),
        (farmer_fac(100), lower_fac(110), False, False, True, True, False),
    ])
    def test_comparisons(self, pop1: Pop, pop2: Pop, gt: bool, ge: bool, lt: bool, le: bool, eq: bool):
        self.assertEqual(pop1 > pop2, gt)
        self.assertEqual(pop1 >= pop2, ge)
        self.assertEqual(pop1 < pop2, lt)
        self.assertEqual(pop1 <= pop2, le)
        self.assertEqual(pop1 == pop2, eq)

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (farmer_fac(100), wheat_fac(100 * LOWER.needs[WHEAT])),
        (miner_fac(100), wheat_fac(100 * LOWER.needs[WHEAT])),
        (specialist_fac(100), wheat_iron_fac(100 * MIDDLE.needs[WHEAT], 100 * MIDDLE.needs[IRON])),

        (farmer_fac(50.55), wheat_fac(D(50.55) * LOWER.needs[WHEAT])),
        (specialist_fac(50.55), wheat_iron_fac(D(50.55) * MIDDLE.needs[WHEAT], D(50.55) * MIDDLE.needs[IRON])),
    ])
    def test_consumption(self, pop: Pop, expected: Stock):
        consumption = pop.calc_consumption()
        self.assert_stocks_equal(consumption, expected)

    @parameterized.expand([
        # LOWER consumes 1 wheat, MIDDLE consumes 2 wheat and 1 iron.
        (farmer_fac(100), wheat_fac(100), D(5/6)),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
        (farmer_fac(100), wheat_fac(50), D(0.5)),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
        (farmer_fac(100), create_stock(), D(1/6)),  # 1/3 * 0.5 + 2/3 * 0 = 1/6

        (specialist_fac(100), wheat_iron_fac(200, 100), D(5/6)),
        (specialist_fac(100), wheat_fac(200), D(0.5)),
        (specialist_fac(100), iron_fac(100), D(0.5)),
        # 1/3 * 0.5 + 2/3 * 0.58r3 = 0.r5
        (specialist_fac(100), wheat_iron_fac(100, 50), D(0.55555555)),
        (specialist_fac(100), create_stock(), D(1/6)),

        (farmer_fac(), create_stock(), D(0)),
        (farmer_fac(), wheat_fac(100), D(0)),
    ])
    def test_welfare(self, pop: Pop, stockpile: Stock, expected: Decimal):
        pop.update_welfare(pop.calc_consumption(), stockpile)
        self.assertAlmostEqual(pop.welfare, expected)

    @parameterized.expand([
        # WELFARE_THRESHOLD = 0.51
        # GROWTH_RATE = 0.05

        (farmer_fac(100, 1), farmer_fac(105, 1)),
        (farmer_fac(100, 0.51), farmer_fac(105, 0.51)),
        (farmer_fac(100), farmer_fac(95)),
        (farmer_fac(100, 0.49), farmer_fac(95, 0.45)),
        (farmer_fac(100, 0), farmer_fac(95)),
    ])
    def test_resize(self, pop: Pop, expected: Pop):
        pop.resize()
        self.assertAlmostEqual(pop.size, expected.size)

    @parameterized.expand([
        (farmer_fac(100, 1), True),
        (farmer_fac(100, 0.51), True),
        (farmer_fac(100), False),
        (farmer_fac(100, 0.49), False),
        (farmer_fac(100, 0), False),

        (middle_fac(100, 1), False),
        (middle_fac(100, 0.51), False),
        (middle_fac(100, 0.5), False),
        (middle_fac(100, 0.49), False),
        (middle_fac(100, 0), False),
    ])
    def test_can_promote(self, pop: Pop, expected: bool):
        self.assertEqual(pop.can_promote(), expected)

    @parameterized.expand([
    # WELFARE_THRESHOLD = 0.51
    # PROMOTE_RATE = 0.01

    (farmer_fac(100, 0.51), middle_fac(1, 0.51)),
    (miner_fac(100, 0.51), middle_fac(1, 0.51)),
    (lower_fac(100, 0.51), middle_fac(1, 0.51)),
    ])
    def test_promote(self, pop: Pop, expected: Pop):
        promoted = pop.promote()

        self.assertEqual(promoted.job, expected.job)
        self.assertEqual(promoted.stratum, expected.stratum)
        self.assertAlmostEqual(promoted.size, expected.size)
        self.assertAlmostEqual(promoted.welfare, expected.welfare)

class TestComFactory(PopMixIn):

    @parameterized.expand([
        ({FARMER: 90, SPECIALIST: 10},
         Commune({FARMER: farmer_fac(90), SPECIALIST: specialist_fac(10)})),
        
        ({FARMER: 90, SPECIALIST: 0}, Commune({FARMER: farmer_fac(90)})),
        ({}, Commune({})),
        (None, Commune({})),
        
        ('test', TypeError),
        ({FARMER: 90, UNEMPLOYED: 10}, ValueError),
        ({LOWER: 90, MIDDLE: 10}, TypeError),
    ])
    def test_create_by_job(self, want: Optional[dict[Jobs, int | float]], expected: type[Exception] | Commune):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, CommuneFactory.create_by_job, want)
        
        else:
            community = CommuneFactory.create_by_job(want)  # type: ignore
            self.assert_communes_equal(community, expected)

    @parameterized.expand([
        ({FARMER: (90, 0.5), SPECIALIST: (10, 0.5)},
         Commune({FARMER: farmer_fac(90, 0.5), SPECIALIST: specialist_fac(10, 0.5)})),
        
        ({FARMER: (90, 1), SPECIALIST: (10, 0)},
         Commune({FARMER: farmer_fac(90, 1), SPECIALIST: specialist_fac(10, 0)})),
        
        ({}, Commune({})),
        (None, Commune({})),
        
        ('test', TypeError),
        ({FARMER: (90, 0.5), UNEMPLOYED: (10, 0.5)}, ValueError),
        ({LOWER: (90, 0.5), MIDDLE: (10, 0.5)}, TypeError),
    ])
    def test_create_by_job_w_w(self, want: Optional[dict[Jobs, tuple[int | float, int | float]]], expected: type[Exception] | Commune):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, CommuneFactory.create_by_job_w_w, want)
        
        else:
            community = CommuneFactory.create_by_job_w_w(want)  # type: ignore
            self.assert_communes_equal(community, expected)

    @parameterized.expand([
        ({LOWER: 90, MIDDLE: 10}, Commune({(LOWER, UNEMPLOYED): lower_fac(90), (MIDDLE, UNEMPLOYED): middle_fac(10)})),
        
        ({LOWER: 90, MIDDLE: 0}, Commune({(LOWER, UNEMPLOYED): lower_fac(90)})),
        ({}, Commune({})),
        (None, Commune({})),
        
        ('test', TypeError),
        ({FARMER: 90, SPECIALIST: 10}, TypeError),
    ])
    def test_create_by_stratum(self, want: Optional[dict[Strata, int | float]], expected: type[Exception] | Commune):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, CommuneFactory.create_by_stratum, want)
        
        else:
            community = CommuneFactory.create_by_stratum(want)  # type: ignore
            self.assert_communes_equal(community, expected)

    @parameterized.expand([
        ({LOWER: (90, 0.5), MIDDLE: (10, 0.5)},
         Commune({(LOWER, UNEMPLOYED): lower_fac(90, 0.5), (MIDDLE, UNEMPLOYED): middle_fac(10, 0.5)})),
        
        ({LOWER: (90, 1), MIDDLE: (10, 0)}, Commune({(LOWER, UNEMPLOYED): lower_fac(90, 1), (MIDDLE, UNEMPLOYED): middle_fac(10, 0)})),

        ({}, Commune({})),
        (None, Commune({})),
        
        ('test', TypeError),
        ({LOWER: 90, SPECIALIST: 10}, TypeError),
    ])
    def test_create_by_stratum_w_w(self, want: Optional[dict[Strata, tuple[int | float, int | float]]], expected: type[Exception] | Commune):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, CommuneFactory.create_by_stratum_w_w, want)
        
        else:
            community = CommuneFactory.create_by_stratum_w_w(want)  # type: ignore
            self.assert_communes_equal(community, expected)

class TestCommunity(PopMixIn, GoodsMixIn):

    @parameterized.expand([
        (c_farmer_fac(100), c_farmer_fac(100), c_farmer_fac(200)),
        (c_farmer_fac(100), c_miner_fac(100), c_farmer_miner_fac(100, 100)),
        (c_farmer_fac(100), CommuneFactory.create_by_job(), c_farmer_fac(100)),

        (c_farmer_fac(100), farmer_fac(100), c_farmer_fac(200)),
        (c_farmer_fac(100), miner_fac(100), c_farmer_miner_fac(100, 100)),

        (c_farmer_fac(100), lower_fac(100), Commune({FARMER: farmer_fac(100), (LOWER, UNEMPLOYED): lower_fac(100)})),
        (c_farmer_fac(100), c_lower_middle_fac(100, 100),
         Commune({FARMER: farmer_fac(100), (LOWER, UNEMPLOYED): lower_fac(100), (MIDDLE, UNEMPLOYED): middle_fac(100)})),

        (c_farmer_fac(100), 'test', TypeError),
    ])
    def test_add(self, com1: Commune, com2: Commune | Pop, expected: type[Exception] | Commune):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, com1.__add__, com2)
        
        else:
            new = com1 + com2
            com1 += com2

            self.assert_communes_equal(new, expected)
            self.assert_communes_equal(com1, expected)

    @parameterized.expand([
        (c_farmer_fac(100), c_farmer_fac(50), c_farmer_fac(50)),
        (c_farmer_fac(100), c_farmer_fac(100), c_farmer_fac(0)),
        (c_farmer_fac(100), c_farmer_fac(0), c_farmer_fac(100)),
        (c_farmer_fac(100), farmer_fac(50, 1), CommuneFactory.create_by_job_w_w({FARMER: (50, 0)})),

        (c_farmer_fac(100), c_miner_fac(100), NegativeAmountError),
        (c_farmer_fac(100), miner_fac(100), NegativeAmountError),
        (c_farmer_fac(100), farmer_fac(101), NegativeAmountError),
        (c_farmer_fac(100), farmer_fac(51, 1), NegativeAmountError),
        (c_farmer_fac(100), lower_fac(100), NegativeAmountError),
        (c_farmer_fac(100), c_farmer_miner_fac(50, 50), NegativeAmountError),
        (c_farmer_fac(100), 'test', TypeError),
    ])
    def test_sub(self, com1: Commune, com2: Commune | Pop, expected: type[Exception] | Commune):

        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, com1.__sub__, com2)
        
        else:
            new = com1 - com2
            com1 -= com2

            self.assert_communes_equal(new, expected)
            self.assert_communes_equal(com1, expected)

    @parameterized.expand([
        (c_farmer_miner_specialist(100, 100, 10), D(210)),
        (c_farmer_miner_fac(100, 100), D(200)),
        (c_farmer_fac(100), D(100)),

        (CommuneFactory.create_by_stratum({LOWER: 100, MIDDLE: 100, UPPER: 10}), D(210)),
        (c_lower_middle_fac(100, 100), D(200)),
        (lower_fac(100), D(100)),

        (c_farmer_fac(100) + CommuneFactory.create_by_stratum({LOWER: 100}), D(200))
    ])
    def test_size(self, community: Commune, expected_size: Decimal):
        self.assertAlmostEqual(community.size, expected_size)
    
    @parameterized.expand([
        (c_farmer_miner_specialist(100, 100, 100), FARMER, D(1/3)),
        (c_farmer_miner_specialist(100, 100, 100), MINER, D(1/3)),
        (c_farmer_miner_specialist(100, 100, 100), SPECIALIST, D(1/3)),
        (c_farmer_miner_specialist(100, 100, 100), LOWER, D(2/3)),
        (c_farmer_miner_specialist(100, 100, 100), MIDDLE, D(1/3)),
        (c_farmer_miner_specialist(100, 100, 100), (LOWER, UNEMPLOYED), D(0)),

        (c_lower_middle_upper_fac(100, 50, 25), LOWER, D(100/175)),
        (c_lower_middle_upper_fac(100, 50, 25), MIDDLE, D(50/175)),
        (c_lower_middle_upper_fac(100, 50, 25), UPPER, D(25/175)),
        (c_lower_middle_upper_fac(100, 50, 25), FARMER, D(0)),
        (c_lower_middle_upper_fac(100, 50, 25), (LOWER, UNEMPLOYED), D(100/175)),
        (c_lower_middle_upper_fac(100, 50, 25), (MIDDLE, UNEMPLOYED), D(50/175)),
        (c_lower_middle_upper_fac(100, 50, 25), (UPPER, UNEMPLOYED), D(25/175)),
    ])
    def test_get_share_of(self, community: Commune, key: Jobs | tuple[Strata, Literal[UNEMPLOYED]] | Strata, expected_share: Decimal):
        self.assertAlmostEqual(community.get_share_of(key), expected_share)
    
    @parameterized.expand([
        (c_farmer_miner_specialist(100, 90, 80), specialist_fac(80)),
        (c_farmer_miner_specialist(79, 90, 80), farmer_fac(79)),
        (c_farmer_miner_specialist(100, 79, 80), miner_fac(79)),
        (c_farmer_miner_specialist(100, 80, 80), miner_fac(80)),
    ])
    def test_min(self, community: Commune, expected: Pop):
        pop = min(community.values())
        self.assert_pops_equal(pop, expected)

    @parameterized.expand([
        (c_farmer_miner_specialist(100, 90, 80), farmer_fac(100)),
        (c_farmer_miner_specialist(100, 90, 101), specialist_fac(101)),
        (c_farmer_miner_specialist(100, 101, 80), miner_fac(101)),
        (c_farmer_miner_specialist(100, 100, 80), farmer_fac(100)),
    ])
    def test_max(self, community: Commune, expected: Pop):
        pop = max(community.values())
        self.assert_pops_equal(pop, expected)

    @parameterized.expand([
        (c_farmer_fac(100), wheat_fac(100 * LOWER.needs[WHEAT])),
        (c_farmer_miner_fac(100, 100), wheat_fac(200 * LOWER.needs[WHEAT])),
        (c_farmer_miner_fac(100, 50), wheat_fac(150 * LOWER.needs[WHEAT])),

        (CommuneFactory.create_by_job({FARMER: 100, SPECIALIST: 100}), 
         wheat_iron_fac(100 * LOWER.needs[WHEAT] + 100 * MIDDLE.needs[WHEAT], 100 * MIDDLE.needs[IRON])),
        (CommuneFactory.create_by_job({FARMER: 100, SPECIALIST: 50}), 
         wheat_iron_fac(100 * LOWER.needs[WHEAT] + 50 * MIDDLE.needs[WHEAT], 50 * MIDDLE.needs[IRON])),
    ])
    def test_calc_goods_demand(self, community: Commune, expected: Stock):
        goods_demand = community.calc_goods_demand()
        self.assert_stocks_equal(goods_demand, expected)

    @parameterized.expand([

        # WELFARE_THRESHOLD = 0.51
        # GROWTH_RATE = 0.05
        # PROMOTE_RATE = 0.01

        (c_farmer_miner_specialist(100, 100, 100), c_farmer_miner_specialist(95, 95, 95)),

        (CommuneFactory.create_by_job_w_w({FARMER: (100, 0.52), MINER: (100, 0.52), SPECIALIST: (100, 0.52)}),
         CommuneFactory.create_by_job_w_w({FARMER: (105, 0.52), MINER: (105, 0.52), SPECIALIST: (105, 0.52)})),

        (CommuneFactory.create_by_job_w_w({FARMER: (100, 0.52), MINER: (100, 0.50), SPECIALIST: (100, 0)}),
         CommuneFactory.create_by_job_w_w({FARMER: (105, 0.52), MINER: (95, 0.50), SPECIALIST: (95, 0)})),
    ])
    def test_resize_all(self, community: Commune, expected: Commune):
        community.resize_all()
        self.assert_communes_equal(community, expected)
    
    @parameterized.expand([

        # PROMOTE_RATE = 0.01

        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 0.52)}), CommuneFactory.create_by_stratum_w_w({MIDDLE: (10, 0.52)})),
        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 0.52), MINER: (1000, 0.52)}), CommuneFactory.create_by_stratum_w_w({MIDDLE: (20, 0.52)})),
        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 1), MINER: (1000, 0.52)}), CommuneFactory.create_by_stratum_w_w({MIDDLE: (20, 0.76)})),
        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 1), MINER: (1000, 0.0)}), CommuneFactory.create_by_stratum_w_w({MIDDLE: (10, 1)})),

        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 0.52), MINER: (1000, 0.52), SPECIALIST: (1000, 0.52)}),
         CommuneFactory.create_by_stratum_w_w({MIDDLE: (20, 0.52)})),
        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 1), MINER: (1000, 0.52), SPECIALIST: (1000, 0.52)}),
         CommuneFactory.create_by_stratum_w_w({MIDDLE: (20, 0.76)})),
        (CommuneFactory.create_by_job_w_w({FARMER: (1000, 1), MINER: (1000, 0), SPECIALIST: (1000, 0.52)}),
         CommuneFactory.create_by_stratum_w_w({MIDDLE: (10, 1)})),
    ])
    def test_promote_all(self, community: Commune, expected: Commune):
        promoted = community.promote_all()
        self.assert_communes_equal(promoted, expected)
    
    @parameterized.expand([
        (c_farmer_fac(100), CommuneFactory.create_by_stratum({LOWER: 100})),

        (c_farmer_miner_fac(100, 100), CommuneFactory.create_by_stratum({LOWER: 200})),

        (c_farmer_miner_specialist(100, 100, 100), c_lower_middle_fac(200, 100)),
    ])
    def test_unemploy_all(self, community: Commune, expected: Commune):
        community.unemploy_all()
        self.assert_communes_equal(community, expected)

    @parameterized.expand([
        (c_farmer_miner_fac(100, 100), LOWER, c_farmer_miner_fac(100, 100)),
        (c_farmer_miner_fac(100, 100), MIDDLE, CommuneFactory.create_by_job()),

        (c_farmer_miner_specialist(100, 100, 100), LOWER, c_farmer_miner_fac(100, 100)),
        (c_farmer_miner_specialist(100, 100, 100), MIDDLE, CommuneFactory.create_by_job({SPECIALIST: 100})),
    ])
    def test_filter(self, community: Commune, filter: Strata, expected: Commune):
        filtered = community[filter]
        self.assert_communes_equal(filtered, expected)
