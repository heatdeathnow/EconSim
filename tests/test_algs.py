from unittest import skip
from parameterized import parameterized
from source.algs import balance_alg, first_in_first_served, impartial, iterative, proportional, retrospective, rich_first
from source.goods import Products, Stock, create_stock
from source.pop import CommuneFactory, Commune, Jobs, Pop, Strata
from source.prod import IndustryFactory, Extractor
from tests import AlgsMixIn
from decimal import getcontext
D = getcontext().create_decimal

WHEAT = Products.WHEAT
IRON = Products.IRON
FLOUR = Products.FLOUR

FARMER = Jobs.FARMER
MINER = Jobs.MINER
SPECIALIST = Jobs.SPECIALIST
UNEMPLOYED = Jobs.UNEMPLOYED

LOWER = Strata.LOWER
MIDDLE = Strata.MIDDLE
UPPER = Strata.UPPER

old_weight = Pop.OLD_WELFARE_WEIGHT
new_weight = Pop.NEW_WELFARE_WEIGHT

wheat_ext = IndustryFactory(WHEAT, {FARMER: 990, SPECIALIST: 10})

com_farmer_miner = CommuneFactory(FARMER, MINER)
com_farmer_specialist = CommuneFactory(FARMER, SPECIALIST)


class TestSharingAlg(AlgsMixIn):
    
    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (com_farmer_miner(100, 100), create_stock({WHEAT: 200}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), MINER: (100, 5/6)}), create_stock()),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
         
        (com_farmer_miner(100, 100), create_stock({WHEAT: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), MINER: (100, 1/6)}), create_stock()),  # 1/3 * 0.5 + 2/3 * 0 = 1/6

        (com_farmer_miner(100, 100), create_stock({WHEAT: 50}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 0.5), MINER: (100, 1/6)}), create_stock()),

        (com_farmer_specialist(100, 100), create_stock({WHEAT: 250, IRON: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), SPECIALIST: (100, 5/6)}), create_stock()),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
         
        (com_farmer_specialist(100, 100), create_stock({WHEAT: 150, IRON: 100}),  # 100 / 150
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), SPECIALIST: (100, '0.611')}), create_stock()),  # 1/3 * 0.5 + 2/3 * 0.r6 = 0.6r1
         
        (com_farmer_specialist(100, 100), create_stock({WHEAT: 175, IRON: 50}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), SPECIALIST: (100, 0.5)}), create_stock()),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
    ])
    def test_first_in_first_served(self, commmunity: Commune, stockpile: Stock, expected: Commune, leftover: Stock):
        self.assert_shares_correctly(first_in_first_served, commmunity, stockpile, expected, leftover)

    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (com_farmer_miner(100, 100), create_stock({WHEAT: 200}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), MINER: (100, 5/6)}), create_stock()),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
         
        (com_farmer_miner(100, 100), create_stock({WHEAT: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 0.5), MINER: (100, 0.5)}), create_stock()),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
         
        (com_farmer_miner(100, 100), create_stock({WHEAT: 50}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, '0.333'), MINER: (100, '0.333')}), create_stock()),  # 1/3 * 0.5 + 2/3 * 0.25 = 0.58r3
         
        (com_farmer_specialist(100, 100), create_stock({WHEAT: 250, IRON: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 5/6), SPECIALIST: (100, '0.611')}), create_stock({WHEAT: 25, IRON: 50})), # 1/3 * 0.5 + 2/3 * 0.r6 = 0.6r1
         
        (com_farmer_specialist(100, 100), create_stock({WHEAT: 137.5, IRON: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, '0.625'), SPECIALIST: (100, '0.486')}), create_stock({IRON: 50})),  # 1/3 * 0.5 + 2/3 * x = 0.486
         
        (com_farmer_specialist(100, 100), create_stock({WHEAT: 100, IRON: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, 0.5), SPECIALIST: (100, '0.444')}), create_stock({IRON: 50})),  # 1/3 * 0.5 + 2/3 * x = 0.444
         
        (CommuneFactory.create_by_job({FARMER: 100, SPECIALIST: 50}), create_stock({WHEAT: 100, IRON: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, '0.611'), SPECIALIST: (50, '0.537')}), create_stock({IRON: '66.667'})),  # 1/3 * 0.5 + 2/3 * .1r5 = 0.444
    ])
    def test_impartial(self, commmunity: Commune, stockpile: Stock, expected: Commune, leftover: Stock):
        self.assert_shares_correctly(impartial, commmunity, stockpile, expected, leftover)

    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3
        # 1/3 * .5 = .1r6

        (com_farmer_miner(100, 100), create_stock({WHEAT: 200}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, D(0.5) * old_weight + new_weight * 100 / LOWER.needs[WHEAT] / 100),
                                           MINER: (100, D(0.5) * old_weight + new_weight * 100 / LOWER.needs[WHEAT] / 100)}), 
         create_stock()),

        (com_farmer_miner(100, 100), create_stock({WHEAT: 100}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, D(0.5) * old_weight + new_weight * 50 / LOWER.needs[WHEAT] / 100),
                                           MINER: (100, D(0.5) * old_weight + new_weight * 50 / LOWER.needs[WHEAT] / 100)}),
         create_stock()),

        (com_farmer_miner(100, 100), create_stock({WHEAT: 50}),
         CommuneFactory.create_by_job_w_w({FARMER: (100, D(0.5) * old_weight + new_weight * 25 / LOWER.needs[WHEAT] / 100),
                                           MINER: (100, D(0.5) * old_weight + new_weight * 25 / LOWER.needs[WHEAT] / 100)}),
         create_stock()),

        (com_farmer_specialist(100, 100), create_stock({WHEAT: 200, IRON: 100}),
         CommuneFactory.create_by_job_w_w(
             {FARMER: (100, D(0.5) * old_weight + new_weight * 50 / LOWER.needs[WHEAT] / 100),
              SPECIALIST: (100, D(0.5) * old_weight + new_weight * (150 / MIDDLE.needs[WHEAT] / 100 + 100 / MIDDLE.needs[IRON] / 100) / 2)}),
         create_stock()),

        (com_farmer_specialist(100, 100), create_stock({WHEAT: 100, IRON: 100}),
         CommuneFactory.create_by_job_w_w(
             {FARMER: (100, D(0.5) * old_weight + new_weight * 0 / LOWER.needs[WHEAT] / 100),
              SPECIALIST: (100, D(0.5) * old_weight + new_weight * (100 / MIDDLE.needs[WHEAT] / 100 + 100 / MIDDLE.needs[IRON] / 100) / 2)}),
         create_stock()),
        
        (CommuneFactory.create_by_job({FARMER: 50, MINER: 100}), create_stock({WHEAT: 150}),
         CommuneFactory.create_by_job_w_w({FARMER: (50, D(0.5) * old_weight + new_weight * 50 / LOWER.needs[WHEAT] / 50),
                                           MINER: (100, D(0.5) * old_weight + new_weight * 100 / LOWER.needs[WHEAT] / 100)}),
         create_stock()),
    ])
    def test_rich_first(self, commmunity: Commune, stockpile: Stock, expected: Commune, leftover: Stock):
        self.assert_shares_correctly(rich_first, commmunity, stockpile, expected, leftover)

    @parameterized.expand([
        # UPPER_WEIGHT  = .50
        # MIDDLE_WEIGHT = .35
        # LOWER_WEIGHT  = .15

        (com_farmer_specialist(100, 100), create_stock({WHEAT: 250, IRON: 100}),
         CommuneFactory.create_by_job_w_w(
             {FARMER: (100, D(0.5) * old_weight + new_weight * 100 / LOWER.needs[WHEAT] / 100),
              SPECIALIST: (100, D(0.5) * old_weight + new_weight * (150 / MIDDLE.needs[WHEAT] / 100 + 85 / MIDDLE.needs[IRON] / 100) / 2)}),
         create_stock({IRON: 15})),
        
        (com_farmer_specialist(100, 100), create_stock({WHEAT: 150, IRON: 100}),
         CommuneFactory.create_by_job_w_w({
             FARMER: (100, D(0.5) * old_weight + new_weight * D(22.5) / LOWER.needs[WHEAT] / 100),
             SPECIALIST: (100, D(0.5) * old_weight + new_weight * (D(127.5) / MIDDLE.needs[WHEAT] / 100 + 85 / MIDDLE.needs[IRON] / 100) / 2)}),
         create_stock({IRON: 15})),

        (CommuneFactory.create_by_job({FARMER: 100, MINER: 50, SPECIALIST: 100}), create_stock({WHEAT: 150, IRON: 100}),
         CommuneFactory.create_by_job_w_w({
             FARMER: (100, D(0.5) * old_weight + new_weight * 15 / LOWER.needs[WHEAT] / 100),
             MINER: (50, D(0.5) * old_weight + new_weight * D(7.5) / LOWER.needs[WHEAT] / 50),
             SPECIALIST: (100, D(0.5) * old_weight + new_weight * (D(127.5) / MIDDLE.needs[WHEAT] / 100 + 85 / MIDDLE.needs[IRON] / 100) / 2)}),
         create_stock({IRON: 15})),
    ])
    def test_proportional(self, commmunity: Commune, stockpile: Stock, expected: Commune, leftover: Stock):
        self.assert_shares_correctly(proportional, commmunity, stockpile, expected, leftover)

class TestBalanceAlg(AlgsMixIn):

    @parameterized.expand([
        (wheat_ext({FARMER: 990, SPECIALIST: 10}), retrospective, Commune({}), wheat_ext({FARMER: 990, SPECIALIST: 10})),
        (wheat_ext(), retrospective, Commune({}), wheat_ext()),
        (wheat_ext({FARMER: 1000}), retrospective, CommuneFactory.create_by_stratum({LOWER: 5.025}), wheat_ext({FARMER: 994.975})),
        (wheat_ext({SPECIALIST: 1000}), retrospective, CommuneFactory.create_by_stratum({MIDDLE: 980.198}), wheat_ext({SPECIALIST: 19.802})),

        (wheat_ext({FARMER: 989, SPECIALIST: 11}), retrospective, CommuneFactory.create_by_stratum({MIDDLE: 0.990}),
         wheat_ext({FARMER: 989, SPECIALIST: 10.01})),

        (IndustryFactory.create_industry(WHEAT, {FARMER: 495, MINER: 495, SPECIALIST: 10}, {FARMER: 500, MINER: 500}), retrospective, 
         CommuneFactory.create_by_stratum({LOWER: 7.796}),
         IndustryFactory.create_industry(WHEAT, {FARMER: 495, MINER: 495, SPECIALIST: 10}, {FARMER: 496.656, MINER: 495.548})),

        (IndustryFactory.create_industry(WHEAT, {FARMER: 495, MINER: 495, SPECIALIST: 10}, {FARMER: 497.5, MINER: 497.5, SPECIALIST: 5}), retrospective,
         CommuneFactory.create_by_stratum({LOWER: 3.898}),
         IndustryFactory.create_industry(WHEAT, {FARMER: 495, MINER: 495, SPECIALIST: 10}, {FARMER: 495.828, MINER: 495.274, SPECIALIST: 5})),

        # 1st - unemploy:  .99r0099   | remain: 999.r0099     | shares: 0.989980178 & 0.010019822
        # 2nd - unemploy:  .019605921 | remain: 998.990295069 | shares: 0.989999607 & 0.010000393
        # 3rd - unemploy:  .000388236 | remain: 998.989906833 | shares: 0.989999992 & 0.010000008
        # to. unemployed: 1.010093167
        (wheat_ext({FARMER: 989, SPECIALIST: 11}), iterative, CommuneFactory.create_by_stratum({MIDDLE: 1.010}), 
         wheat_ext({FARMER: 989, SPECIALIST: 9.99})),
    ])
    def test_balance(self, extractor: Extractor, alg: balance_alg, expected_unemployed: Commune, expected_extractor: Extractor):
        self.assert_balances_correctly(alg, extractor, expected_unemployed, expected_extractor)
