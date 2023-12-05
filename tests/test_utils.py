from typing import Literal, Optional, Sequence
from parameterized import parameterized
from unittest import TestCase, skip
from source.goods import Goods, Stockpile

from source.pop import ComFactory, Community, Jobs
from source.utils import FirstInFirstServed, Impartial, RichFirst, SharingAlg

class TestSharingAlg(TestCase):

    def __test_alg(self, algorithm: type[SharingAlg], commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        algorithm.share(commmunity, stockpile)

        self.assertEqual(len(commmunity), len(expected))
        for jobs, pop in commmunity.items():
            pop_ = expected[jobs]

            self.assertAlmostEqual(pop.welfare, pop_.welfare)
        
        self.assertEqual(len(stockpile), len(leftover))
        for good, amount in stockpile.items():
            self.assertEqual(amount, leftover[good])
    
    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 200}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
            Stockpile()
        ),
        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 1/6)}),  # 1/3 * 0.5 + 2/3 * 0 = 1/6
            Stockpile()
        ),
        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 50}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.MINER: (100, 1/6)}),
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 300, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 150, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 0.58333333)}),  # 1/3 * 0.5 + 2/3 * 0.625 = 0.5833...
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 0.5)}),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
            Stockpile()
        ),
    ])
    def test_first_in_first_served(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(FirstInFirstServed, commmunity, stockpile, expected, leftover)

    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 200}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
            Stockpile()
        ),
        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.MINER: (100, 0.5)}),  # 1/3 * 0.5 + 2/3 * 0.5 = 0.5
            Stockpile()
        ),
        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 50}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.33333333), Jobs.MINER: (100, 0.33333333)}),  # 1/3 * 0.5 + 2/3 * 0.25 = 0.5833333
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 300, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 0.58333333)}),  # 1/3 * 0.5 + 2/3 * 0.625 = 0.5833333
            Stockpile({Goods.WHEAT: 50, Goods.IRON: 50})
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 150, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.66666666), Jobs.SPECIALIST: (100, 0.45833333)}),  # 1/3 * 0.5 + 2/3 * 0.4375 = 0.4583333
            Stockpile({Goods.IRON: 50})
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.SPECIALIST: (100, 0.41666666)}),  # 1/3 * 0.5 + 2/3 * 0.4375 = 0.4166666
            Stockpile({Goods.IRON: 50})
        ),
    ])
    def test_impartial(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(Impartial, commmunity, stockpile, expected, leftover)
    
    @parameterized.expand([

        # OLD_WELFARE_WEIGHT = 1/3
        # NEW_WELFARE_WEIGHT = 2/3

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 200}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.MINER: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
            Stockpile()
        ),
        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.5), Jobs.MINER: (100, 0.5)}),  # 1/3 * 0.5 + 0.5 * 0 = 0.5
            Stockpile()
        ),
        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.MINER: 100}),
            Stockpile({Goods.WHEAT: 50}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.33333333), Jobs.MINER: (100, 0.33333333)}),  # 1/3 * 0.5 + 0.25 * 0 = 0.333...
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 300, Goods.IRON: 100}),
            ComFactory.job_welfare({Jobs.FARMER: (100, 5/6), Jobs.SPECIALIST: (100, 5/6)}),  # 1/3 * 0.5 + 2/3 * 1 = 5/6
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 150, Goods.IRON: 100}),                                         # 1/3 * 0.5 + 2/3 * 7/8 = 0.75
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.16666666), Jobs.SPECIALIST: (100, 0.75)}),  # 1/3 * 0.5 + 2/3 * 0 = 0.166...
            Stockpile()
        ),

        (
            ComFactory.job({Jobs.FARMER: 100, Jobs.SPECIALIST: 100}),
            Stockpile({Goods.WHEAT: 100, Goods.IRON: 100}),                                               # 1/3 * 0.5 + 2/3 * 0.75 = 0.666...
            ComFactory.job_welfare({Jobs.FARMER: (100, 0.16666666), Jobs.SPECIALIST: (100, 0.66666666)}),  # 1/3 * 0.5 + 2/3 * 0 = 0.166...
            Stockpile()
        ),
    ])
    def test_rich_first(self, commmunity: Community, stockpile: Stockpile, expected: Community, leftover: Stockpile):
        self.__test_alg(RichFirst, commmunity, stockpile, expected, leftover)
    
    def test_proportional(self):
        pass
