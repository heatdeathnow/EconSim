import copy
from parameterized import parameterized
from unittest import TestCase, skip
from source import ABS_TOL, DECIMAL_CASES
from source.goods import Goods, Stockpile

from source.pop import ComFactory, Community, Jobs, Pop, Strata
from source.prod import ExtFactory, Extractor
from source.utils import BalanceAlg, FirstInFirstServed, Impartial, Iterative, Proportional, Retrospective, RichFirst, SharingAlg

class TestSharingAlg(TestCase):

    def __test_alg(self, algorithm: type[SharingAlg], commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        algorithm.share(commmunity, stockpile)

        self.assertEqual(len(commmunity), len(expected))
        for jobs, pop in commmunity.items():
            pop_ = expected[jobs]
            
            self.assertAlmostEqual(pop.welfare, pop_.welfare, DECIMAL_CASES)
        
        self.assertEqual(len(stockpile), len(leftover))
        for good, amount in stockpile.items():
            self.assertEqual(amount, leftover[good])
    
    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 200}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 1/6)}),  # 1/3 * 0.5 + 2/3 * 0 = 1/6
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 50}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.MINER: (100, 1/6)}),
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 250, Goods.IRON: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 150, Goods.IRON: 100}),  # 100 / 150
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 0.611)}),  # 1/3 * 0.5 + 2/3 * 0.r6 = 0.6r1
         Stockpile()
        ),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 175, Goods.IRON: 50}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 0.5)}),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
         Stockpile()),
    ])
    def test_first_in_first_served(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(FirstInFirstServed, commmunity, stockpile, expected, leftover)

    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 200}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.MINER: (100, 0.5)}),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 50}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 0.333), Jobs.MINER: (100, 0.333)}),  # 1/3 * 0.5 + 2/3 * 0.25 = 0.58r3
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 250, Goods.IRON: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 0.611)}),  # 1/3 * 0.5 + 2/3 * 0.r6 = 0.6r1
         Stockpile({Goods.WHEAT: 25, Goods.IRON: 50})),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 137.5, Goods.IRON: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 0.625), Jobs.SPECIALIST: (100, 0.486)}),  # 1/3 * 0.5 + 2/3 * x = 0.486
         Stockpile({Goods.IRON: 50})),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.SPECIALIST: (100, 0.444)}),  # 1/3 * 0.5 + 2/3 * x = 0.444
         Stockpile({Goods.IRON: 50})),
        
        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 50}),
         Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}),
         ComFactory.job_welfare({Jobs.FARMER: (100, 0.611), Jobs.SPECIALIST: (100, 0.537)}),  # 1/3 * 0.5 + 2/3 * .1r5 = 0.444
         Stockpile({Goods.IRON: 66.667})),
    ])
    def test_impartial(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(Impartial, commmunity, stockpile, expected, leftover)

    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3
        # 1/3 * .5 = .1r6

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 200}),                         # goods | needed | popsize
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 100 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.MINER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 100 / Strata.LOWER.needs[Goods.WHEAT] / 100)}),
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 100}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 50 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.MINER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 50 / Strata.LOWER.needs[Goods.WHEAT] / 100)}),
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 50}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 25 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.MINER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 25 / Strata.LOWER.needs[Goods.WHEAT] / 100)}),
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 200, Goods.IRON: 100}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 50 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.SPECIALIST: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * (150 / Strata.MIDDLE.needs[Goods.WHEAT] / 100 + 100 / Strata.MIDDLE.needs[Goods.IRON] / 100) / 2)}),
         Stockpile()),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 0 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.SPECIALIST: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * (100 / Strata.MIDDLE.needs[Goods.WHEAT] / 100 + 100 / Strata.MIDDLE.needs[Goods.IRON] / 100) / 2)}),
         Stockpile()),
        
        (ComFactory.job({Jobs.FARMER: 50, Jobs.MINER: 100}),
         Stockpile({Goods.WHEAT: 150}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 50 / Strata.LOWER.needs[Goods.WHEAT] / 50),
              Jobs.MINER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 100 / Strata.LOWER.needs[Goods.WHEAT] / 100)}),
         Stockpile()),
    ])
    def test_rich_first(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(RichFirst, commmunity, stockpile, expected, leftover)

    @parameterized.expand([
        # UPPER_WEIGHT  = .50
        # MIDDLE_WEIGHT = .35
        # LOWER_WEIGHT  = .15

        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 250, Goods.IRON: 100}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 100 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.SPECIALIST: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * (150 / Strata.MIDDLE.needs[Goods.WHEAT] / 100 + 85 / Strata.MIDDLE.needs[Goods.IRON] / 100) / 2)}),
         Stockpile({Goods.IRON: 15})),
        
        (ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 150, Goods.IRON: 100}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 22.5 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.SPECIALIST: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * (127.5 / Strata.MIDDLE.needs[Goods.WHEAT] / 100 + 85 / Strata.MIDDLE.needs[Goods.IRON] / 100) / 2)}),
         Stockpile({Goods.IRON: 15})),

        (ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 50, Jobs.SPECIALIST: 100}),
         Stockpile({Goods.WHEAT: 150, Goods.IRON: 100}),
         ComFactory.job_welfare(
             {Jobs.FARMER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 15 / Strata.LOWER.needs[Goods.WHEAT] / 100),
              Jobs.MINER: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * 7.5 / Strata.LOWER.needs[Goods.WHEAT] / 50),
              Jobs.SPECIALIST: (100, 0.5 * Pop.OLD_WELFARE_WEIGHT + Pop.NEW_WELFARE_WEIGHT * (127.5 / Strata.MIDDLE.needs[Goods.WHEAT] / 100 + 85 / Strata.MIDDLE.needs[Goods.IRON] / 100) / 2)}),
         Stockpile({Goods.IRON: 15})),
    ])
    def test_proportional(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(Proportional, commmunity, stockpile, expected, leftover)

class TestBalanceAlg(TestCase):

    @parameterized.expand([
        (ExtFactory.full(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Retrospective, Community()),
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}), Retrospective, Community()),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 1000}), Retrospective,
         ComFactory.stratum({Strata.LOWER: 5.025})),  # This will be changed.
        
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.SPECIALIST: 1000}), Retrospective,
         ComFactory.stratum({Strata.MIDDLE: 980.198})),  # This will be changed.

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 989, Jobs.SPECIALIST: 11}), Retrospective,
         ComFactory.stratum({Strata.MIDDLE: 0.990})),

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 495, Jobs.MINER: 495, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 500, Jobs.MINER: 500}), 
          Retrospective, ComFactory.stratum({Strata.LOWER: 7.796})),  # This will be changed.

        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 495, Jobs.MINER: 495, Jobs.SPECIALIST: 10}, 
                            {Jobs.FARMER: 497.5, Jobs.MINER: 497.5, Jobs.SPECIALIST: 5}), Retrospective,
         ComFactory.stratum({Strata.LOWER: 3.898})),

        # 1st - unemploy:  .99r0099   | remain: 999.r0099     | shares: 0.989980178 & 0.010019822
        # 2nd - unemploy:  .019605921 | remain: 998.990295069 | shares: 0.989999607 & 0.010000393
        # 3rd - unemploy:  .000388236 | remain: 998.989906833 | shares: 0.989999992 & 0.010000008
        # to. unemployed: 1.010093167
        (ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 990, Jobs.SPECIALIST: 10}, {Jobs.FARMER: 989, Jobs.SPECIALIST: 11}), Iterative,
         ComFactory.stratum({Strata.MIDDLE: 1.010})),  # This will result in a error because the third iteration is too small.
    ])
    def test_balance(self, extractor: Extractor, alg: type[BalanceAlg], expected: Community):
        original_size = extractor.workforce.size
        unemployed = extractor.balance(alg)

        for stratum in Strata:
            self.assertAlmostEqual(unemployed[stratum, Jobs.NONE].size, expected[stratum, Jobs.NONE].size)
            self.assertAlmostEqual(unemployed[stratum, Jobs.NONE].welfare, expected[stratum, Jobs.NONE].welfare)

        self.assertAlmostEqual(extractor.workforce.size, original_size - unemployed.size)
