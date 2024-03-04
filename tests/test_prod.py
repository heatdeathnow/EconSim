from decimal import Decimal, getcontext
from unittest import skip
from tests import Q
from source.pop import CommuneFactory, Commune, Jobs, Pop, Strata, PopFactory
from source.exceptions import CannotEmployError
from source.prod import IndustryFactory, Extractor, Manufactury
from source.goods import ProdTech, Products, Stock, create_stock, stock_factory
from parameterized import parameterized
from tests import ProdMixIn
D = getcontext().create_decimal

EXTRACTION = ProdTech.EXTRACTION
CRAFTING = ProdTech.CRAFTING
MILLING = ProdTech.MILLING

WHEAT = Products.WHEAT
IRON = Products.IRON
FLOUR = Products.FLOUR

UNEMPLOYED = Jobs.UNEMPLOYED
FARMER = Jobs.FARMER
MINER = Jobs.MINER
CRAFTSMAN = Jobs.CRAFTSMAN
SPECIALIST = Jobs.SPECIALIST

LOWER = Strata.LOWER
MIDDLE = Strata.MIDDLE
UPPER = Strata.UPPER

farmer_fac = PopFactory(FARMER)
miner_fac = PopFactory(MINER)
specialist_fac = PopFactory(SPECIALIST)

lower_fac = PopFactory(LOWER)
middle_fac = PopFactory(MIDDLE)
upper_fac = PopFactory(UPPER)

flour_stock_fac = stock_factory(FLOUR)

wheat_ext = IndustryFactory(WHEAT, {FARMER: 990, SPECIALIST: 10})
iron_ext = IndustryFactory(IRON, {MINER: 990, SPECIALIST: 10})
flour_craft = IndustryFactory(FLOUR, {CRAFTSMAN: 990, SPECIALIST: 10}, CRAFTING)
flour_mill = IndustryFactory(FLOUR, {CRAFTSMAN: 990, SPECIALIST: 10}, MILLING)

flour_craft_yield = FLOUR.prod_techs[CRAFTING].base_yield
flour_mill_yield = FLOUR.prod_techs[MILLING].base_yield

class TestExtractor(ProdMixIn):

    @parameterized.expand([
        (wheat_ext(), 1000),
        (IndustryFactory.create_industry(WHEAT, {FARMER: 500, MINER: 500}), 1000),
        (IndustryFactory.create_industry(WHEAT, {FARMER: 250, MINER: 500}), 750),
    ])
    def test_capacity(self, extractor: Extractor, expected: Decimal):
        self.assertAlmostEqual(extractor.capacity, expected)

    @parameterized.expand([
        (wheat_ext(), {FARMER: D('0.99'), SPECIALIST: D('0.01')}),
        (wheat_ext({FARMER: 900, SPECIALIST: 100}), {FARMER: D('0.99'), SPECIALIST: D('0.01')}),
        (IndustryFactory.create_industry(WHEAT, {FARMER: 450, MINER: 450, SPECIALIST: 100}), 
         {FARMER: D('0.45'), MINER: D('0.45'), SPECIALIST: D('0.1')}),
    ])
    def test_efficient_shares(self, extractor: Extractor, expected: dict[Jobs, Decimal]):
        self.assertEqual(len(extractor.efficient_shares), len(expected))
        self.assertAlmostEqual(sum(extractor.efficient_shares.values()), 1)

        for job, share in extractor.efficient_shares.items():
            self.assertTrue(share >= D(0))
            self.assertTrue(share <= D(1))

            self.assertAlmostEqual(share, expected[job])

    @parameterized.expand([
        (wheat_ext(), D(0)),

        (wheat_ext({FARMER: 990, SPECIALIST: 10}), D(1)),

        # size: 500
        # efficient_shares --- farmer: 990/1000 = .99 | specialist: 10/1000 = .01
        # shares           --- farmer: 495/500  = .99 | specialist: 5 / 500 = .01
        (wheat_ext({FARMER: 495, SPECIALIST: 5}), D(1)),

        # size: 505
        # efficient_shares    --- farmer: 990/1000       = .99      | specialist: 10/1000        = .01
        # shares              --- farmer: 495/505        = .r9801   | specialist: 10 / 505       = .r0198
        # difference          --- farmer: .99 - .r9801   = .00r9801 | specialist: .r0198 - .01   = .00r9801
        # weighted difference --- farmer: .00r9801 / .99 = .r0099   | specialist: .00r9801 / .01 = .r9801
        # efficiency          --- 1 - (.r0099 + .r9801) / 2 = .r5049
        (wheat_ext({FARMER: 495, SPECIALIST: 10}), D('0.50495049')),

        # size: 1000
        # efficient_shares    --- farmer: 990/1000  = .99  | specialist: 10/1000   = .01
        # shares              --- farmer: 1000/1000 = 1    | specialist: 0 / 1000  = 0
        # difference          --- farmer: 1 - .99   = .01  | specialist: .01 - 0   = .01
        # weighted difference --- farmer: .01 / .99 = .r01 | specialist: .01 / .01 = 1
        # efficiency          --- 1 - (.r01 + 1) / 2 = .r49
        (wheat_ext({FARMER: 1000}), D('0.49494949')),

        # size: 495
        # efficient_shares    --- farmer: 990/1000   = .99  | specialist: 10/1000   = .01
        # shares              --- farmer: 495/495    = 1    | specialist: 0 / 495   = 0
        # difference          --- farmer: 1 - 0.99   = .01  | specialist: .01 - 0   = .01
        # weighted difference --- farmer: .01 / .99  = .r01 | specialist: .01 / .01 = 1
        # efficiency          --- 1 - (.r01 + 1) / 2 = .r49
        (wheat_ext({FARMER: 495}), D('0.49494949')),
        
        # size: 10
        # efficient_shares    --- farmer: 990/1000  = .99 | specialist: 10/1000   = .01
        # shares              --- farmer: 0  /  10  = 0   | specialist: 10 / 10   = 1
        # difference          --- farmer: .99 - 0   = .99 | specialist: 1 - .01   = .99
        # weighted difference --- farmer: .99 / .99 = 1   | specialist: .99 / .01 = 1
        # efficiency          --- 1 - (1 + 1) / 2   = 0
        (wheat_ext({SPECIALIST: 10}), D(0)),

        # size: 5
        # efficient_shares    --- farmer: 990/1000  = .99 | specialist: 10/1000   = .01
        # shares              --- farmer: 0  /  5   = 0   | specialist: 5 /   5   = 1
        # difference          --- farmer: .99 - 0   = .99 | specialist: 1 - .01   = .99
        # weighted difference --- farmer: .99 / .99 = 1   | specialist: .99 / .01 = 1
        # efficiency          --- 1 - (1 + 1) / 2   = 0
        (wheat_ext({SPECIALIST: 5}), D(0)),
    ])
    def test_calc_efficiency(self, extractor: Extractor, expected: Decimal):
        self.assertAlmostEqual(extractor.calc_efficiency(), expected)
    
    @parameterized.expand([
        # Current fixed throughput (will be changed in the future.): THROUGHPUT = 1.25
        # base_yield * self.calc_total_workers() * self.calc_efficiency()

        (wheat_ext(), create_stock()),

        # base_yield * size * efficiency
        (wheat_ext({FARMER: 990, SPECIALIST: 10}), 
         create_stock({WHEAT: 1000 * WHEAT.prod_techs[EXTRACTION].base_yield})),
        (iron_ext({MINER: 990, SPECIALIST: 10}), 
         create_stock({IRON: 1000 * IRON.prod_techs[EXTRACTION].base_yield})),

        # base_yield * size * 0.r49
        (wheat_ext({FARMER: 1000}),
         create_stock({WHEAT: D(1000) * WHEAT.prod_techs[EXTRACTION].base_yield * D('0.49494949')})),
        
        # base_yield * size * 0.r49
        (wheat_ext({FARMER: 990}),
         create_stock({WHEAT: D(990) * WHEAT.prod_techs[EXTRACTION].base_yield * D('0.49494949')})),

        # base_yield * size * 0
        (wheat_ext({SPECIALIST: 10}), create_stock()),
        
        # base_yield * size * 0.r49 = 306.25
        (wheat_ext({FARMER: 495}),
         create_stock({WHEAT: D(495) * WHEAT.prod_techs[EXTRACTION].base_yield * D('0.49494949')})),

        # base_yield * 5 * 0 = 0
        (wheat_ext({SPECIALIST: 5}), create_stock()),

        # base_yield * 500 * 1 = 625
        (wheat_ext({FARMER: 495, SPECIALIST: 5}),
         create_stock({WHEAT: 500 * WHEAT.prod_techs[EXTRACTION].base_yield})),
        
        # size: 500
        # efficient_shares    --- farmer: 990/1000   = .99  | specialist: 10/1000   = .01
        # shares              --- farmer: 400/500    = .8   | specialist: 100/500   = .2
        # difference          --- farmer: .99 - .8   = .19  | specialist: .2 - .01  = .19
        # weighted difference --- farmer: .19 / .99  = .r19 | specialist: .19 / .01 = 1
        # efficiency          --- 1 - (.r19 + 1) / 2 = 0.r40
        # production          --- base_yield * 500 * 0.r40
        (wheat_ext({FARMER: 400, SPECIALIST: 100}),
         create_stock({WHEAT: D(500) * WHEAT.prod_techs[EXTRACTION].base_yield * D('0.40404040')})),
    ])
    def test_produce(self, extractor: Extractor, expected: Stock):
        stockpile = extractor.produce()
        self.assert_stocks_equal(stockpile, expected)
    
    @parameterized.expand([
        (wheat_ext({FARMER: 990, SPECIALIST: 10}), {}),

        (wheat_ext(), {FARMER: 990, SPECIALIST: 10}),

        (wheat_ext({FARMER: 495, SPECIALIST: 5}), {FARMER: 495, SPECIALIST: 5}),
        
        (wheat_ext({FARMER: 990}), {SPECIALIST: 10}),
        
        (wheat_ext({FARMER: 1000}), {}),

        (wheat_ext({SPECIALIST: 500}), {FARMER: 500}),
    ])
    def test_calc_labor_demand(self, extractor: Extractor, expected: dict[Jobs, int | float]):
        labor_demand = extractor.calc_labor_demand()

        self.assertEqual(len(labor_demand), len(expected))
        for job, need in labor_demand.items():
            self.assertAlmostEqual(need.size, expected[job])  # type: ignore

    @parameterized.expand([
        (wheat_ext(), farmer_fac(100), CannotEmployError),
        (wheat_ext(), miner_fac(100), CannotEmployError),
        (wheat_ext(), specialist_fac(100), CannotEmployError),
        (wheat_ext(), lower_fac(100), True),
        (wheat_ext(), middle_fac(100), True),
        (wheat_ext(), upper_fac(100), False),

        (wheat_ext({FARMER: 990, SPECIALIST: 10}), lower_fac(100), False),
        (wheat_ext({FARMER: 980, SPECIALIST: 10}), 
         lower_fac(100), True),
    ])
    def test_can_employ(self, extractor: Extractor, pop: Pop, expected: bool | type[Exception]):
        if isinstance(expected, type) and issubclass(expected, Exception):
            self.assertRaises(expected, extractor.can_employ, pop)
        
        else:
            self.assertTrue(extractor.can_employ(pop) == expected)

    @parameterized.expand([
        (wheat_ext(), lower_fac(100), wheat_ext({FARMER: 100}), lower_fac()),
        (wheat_ext(), middle_fac(100), wheat_ext({SPECIALIST: 10}), middle_fac(90)),
        (wheat_ext(), lower_fac(1000), wheat_ext({FARMER: 990}), lower_fac(10)),
        (wheat_ext(), lower_fac(100), wheat_ext({FARMER: 100}), lower_fac()),
        (wheat_ext(), middle_fac(100), wheat_ext({SPECIALIST: 10}), middle_fac(90)),
        (wheat_ext({FARMER: 940, SPECIALIST: 10}), lower_fac(100), wheat_ext({FARMER: 990, SPECIALIST: 10}), lower_fac(50))
    ])
    def test_employ(self, extractor: Extractor, pop: Pop, expected_extractor: Extractor, expected_pop: Pop):
        extractor.employ(pop)

        self.assert_pops_equal(pop, expected_pop)
        self.assert_industries_equal(extractor, expected_extractor)

    @parameterized.expand([
        (wheat_ext({FARMER:495, SPECIALIST: 10}), True),
        (wheat_ext({FARMER: 990, SPECIALIST: 10}), False),
        (wheat_ext({FARMER:495, SPECIALIST: 5}), False),
    ])
    def test_is_unbalanced(self, extractor: Extractor, expected: bool):
        self.assertTrue(extractor.is_unbalanced() == expected)

    @parameterized.expand([
        (Extractor(WHEAT, EXTRACTION, WHEAT.prod_techs[EXTRACTION], {FARMER: D(990), SPECIALIST: D(10)}, 
                   CommuneFactory.create_by_job({FARMER: 1980, SPECIALIST: 20})),
                   CommuneFactory.create_by_stratum({Strata.LOWER: 990, Strata.MIDDLE: 10}),
         wheat_ext({FARMER: 990, SPECIALIST: 10})),

        (Extractor(WHEAT, EXTRACTION, WHEAT.prod_techs[EXTRACTION], {FARMER: D(990), SPECIALIST: D(10)}, 
                   CommuneFactory.create_by_job({FARMER: 900, SPECIALIST: 200})),
                   CommuneFactory.create_by_stratum({Strata.LOWER: 81.818181818, Strata.MIDDLE: 18.181818182}),
         wheat_ext({FARMER: 818.18181818, SPECIALIST: 181.81818182}))
    ])
    def test_fire_excess(self, extractor: Extractor, expected_unemployed: Commune, expected_extractor: Extractor):
        unemployed = extractor.fire_excess()

        self.assert_communes_equal(unemployed, expected_unemployed)
        self.assert_industries_equal(extractor, expected_extractor)

class TestManufactury(ProdMixIn):

    @parameterized.expand([
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}), 1000 * flour_craft_yield * 1),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}), 1000 * flour_mill_yield * 1),
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 5}), 500 * flour_craft_yield * 1),
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 10}), 505 * flour_craft_yield * D('0.50495049')),
    ])
    def test_calc_potential_production(self, manufactury: Manufactury, expected: Decimal):
        self.assertAlmostEqual(manufactury.calc_potential_production(), expected, delta=Q)

    @parameterized.expand([
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000, IRON: 1000}), 1),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 880, IRON: 220}), 1),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 800, IRON: 100}), D(100/220)),
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 5}, {WHEAT: 500, IRON: 500}), 1),
        # eff 1 | 0.2 * 550 = 110 ||| 0.8 * 550 = 
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 5}, {WHEAT: 400, IRON: 50}), D(50/110)),
        #  eff D('0.50495049') = 280.5 | 0.2 * 280.5 = 56.1
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 10}, {WHEAT: 400, IRON: 50}), D(50/56.1)),

        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000, IRON: 1000}), 1),
        #  1000 * flour_mill_yield = 1500 | 0.35 * 1500 = 525 | 0.65 * 1500 = 975
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 975, IRON: 525}), 1),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 650, IRON: 350}), D(650/975)),
    ])
    def test_calc_ceil(self, manufactury: Manufactury, expected: Decimal):
        self.assertAlmostEqual(manufactury.calc_ceil(), expected, delta=Q)

    @parameterized.expand([
        #  Production(1.1, {Products.WHEAT: 0.8, Products.IRON: 0.2})
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000, IRON: 1000}), flour_stock_fac(1000 * flour_craft_yield * 1)),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 880, IRON: 220}), flour_stock_fac(1000 * flour_craft_yield * 1)),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 800, IRON: 100}), flour_stock_fac(1000 * flour_craft_yield * 1 * D(100/220))),
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 5}, {WHEAT: 400, IRON: 50}), 
         flour_stock_fac(500 * flour_craft_yield * 1 * D(100/220))),
        (flour_craft({CRAFTSMAN: 495, SPECIALIST: 10}, {WHEAT: 400, IRON: 50}), 
         flour_stock_fac(D(505) * flour_craft_yield * D(50/56.1) * D('0.50495049'))),
        
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 975, IRON: 525}), flour_stock_fac(1000 * flour_mill_yield)),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 650, IRON: 350}), flour_stock_fac(1000 * flour_mill_yield * D(650/975))),
    ])
    def test_produce(self, manufactury: Manufactury, expected: Stock):
        self.assert_stocks_equal(manufactury.produce(), expected)
    
    @parameterized.expand([
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000, IRON: 1000}), create_stock()),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}), create_stock({WHEAT: 880, IRON: 220})),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 440, IRON: 110}), create_stock({WHEAT: 440, IRON: 110})),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 340, IRON: 110}), create_stock({WHEAT: 540, IRON: 110})),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000}), create_stock({IRON: 220})),

        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000, IRON: 1000}), create_stock()),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}), create_stock({WHEAT: 975, IRON: 525})),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 487.5, IRON: 262.5}), create_stock({WHEAT: 487.5, IRON: 262.5})),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 387.5, IRON: 262.5}), create_stock({WHEAT: 587.5, IRON: 262.5})),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000}), create_stock({IRON: 525})),
    ])
    def test_calc_input_demand(self, manufactury: Manufactury, demand: Stock):
        self.assert_stocks_equal(manufactury.calc_input_demand(), demand)

    @parameterized.expand([
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}), create_stock({WHEAT: 880, IRON: 220}), 
         create_stock({WHEAT: 880, IRON: 220}), create_stock()),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}), create_stock({WHEAT: 440, IRON: 110}), 
         create_stock({WHEAT: 440, IRON: 110}), create_stock()),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}), create_stock({WHEAT: 1000, IRON: 1000}), 
         create_stock({WHEAT: 880, IRON: 220}), create_stock({WHEAT: 120, IRON: 780})),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 1000}), create_stock({WHEAT: 1000, IRON: 1000}), 
         create_stock({WHEAT: 1000, IRON: 220}), create_stock({WHEAT: 1000, IRON: 780})),
        (flour_craft({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 500}), create_stock({WHEAT: 1000, IRON: 1000}), 
         create_stock({WHEAT: 880, IRON: 220}), create_stock({WHEAT: 620, IRON: 780})),
        
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}), create_stock({WHEAT: 975, IRON: 525}),
         create_stock({WHEAT: 975, IRON: 525}), create_stock()),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 100, IRON: 50}), create_stock({WHEAT: 500, IRON: 500}),
         create_stock({WHEAT: 600, IRON: 525}), create_stock({IRON: 25})),
        (flour_mill({CRAFTSMAN: 990, SPECIALIST: 10}, {WHEAT: 100, IRON: 50}), create_stock({WHEAT: 900, IRON: 500}),
         create_stock({WHEAT: 975, IRON: 525}), create_stock({WHEAT: 25, IRON: 25})),
    ])
    def test_restock(self, manufactury: Manufactury, stock: Stock, exp_manu_stock: Stock, exp_stock: Stock):
        manufactury.restock(stock)
        self.assert_stocks_equal(manufactury.stockpile, exp_manu_stock)
        self.assert_stocks_equal(stock, exp_stock)

    @parameterized.expand([])
    def test_produce(self):
        self.fail()
        