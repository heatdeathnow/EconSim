from os.path import join, dirname, abspath
from os import system
from sys import path

main_module_path = abspath(join(dirname(__file__), '..'))
path.insert(0, main_module_path)

import variables as v
v.TESTING = True
###########################################################################################################################################

from unittest import TestCase, main, skip
from parameterized import parameterized
from terrain import Biome
from variables import BIOMES
from production import *
from abc import ABC
from typing import Optional

class IndustryTest(ABC):

    @abstractmethod
    def test_get_total_workers(self, extractor: Extractor, expected: float):
        total_workers = extractor.get_total_workers()
        self.assertEqual(total_workers, expected)

    @abstractmethod
    def test_get_real_proportion(self, extractor: Extractor, expected: dict[str, float]) -> None:
        real_proportion = extractor.get_real_proportion()
        self.assertEqual(real_proportion, expected)

    @abstractmethod
    def test_get_labor_demand(self, extractor: Extractor, expected: dict[str, float]) -> None:
        labor_demand = extractor.get_labor_demand()

        for (key1, val1), (key2, val2) in zip(labor_demand.items(), expected.items()):
            self.assertEqual(key1, key2)
            self.assertAlmostEqual(val1, val2)

    @abstractmethod
    def test_distribute_workers(self, industry: str, workers: tuple[Population, ...], expected: dict[str, float] | None) -> None:
        self.industries: Extractor

        try:
            self.industries[industry].distribute_workers(*workers)
            self.assertEqual(self.industries[industry].workers, expected)            

        except ValueError:
            if expected is None:
                pass

            else:
                self.fail()
    
    @abstractmethod
    def test_get_correct_sizes(self, extractor: Extractor, expected: dict[str, float]):
        correct_sizes = extractor.get_correct_sizes()

        for x, y in zip(correct_sizes.values(), expected.values()):
            self.assertAlmostEqual(x, y)

    @abstractmethod
    def test_get_fix_proportion(self, extractor: Extractor, expected: dict[str, float]) -> None:
        new_workers = extractor.get_fix_proportion()

        self.assertEqual(len(new_workers), len(expected))

        for (key1, val1), (key2, val2) in zip(new_workers.items(), expected.items()):
            self.assertEqual(key1, key2)
            self.assertAlmostEqual(val1, val2)

    @abstractmethod
    def test_get_production(self, extractor: Extractor, expected: float):
        amount = extractor.get_production()
        self.assertAlmostEqual(amount, expected)

    @abstractmethod
    def test_get_goods_demand(self, extractor: Extractor, expected: dict[str, float], stratum: Optional[v.Strata] = None) -> None:
        goods_demand = extractor.get_goods_demand(stratum)

        self.assertEqual(len(goods_demand), len(expected))
        for (real_good, real_amount), (expected_good, expected_amount) in zip(goods_demand.items(), expected.items()):
            self.assertEqual(real_good, expected_good)
            self.assertAlmostEqual(real_amount, expected_amount)

class ExtractorTest(IndustryTest, TestCase):

    def setUp(self) -> None:
        self.industries = {
            'just_farmer': Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )),
            'farmer_miner' : Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(250, 'Farmer'), LowerStrata(250, 'Miner'),)),
        }

    def tearDown(self) -> None:
        del self.industries

    @parameterized.expand([
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(1000, 'Farmer'), )), 
         1000),
        (Extractor('grain', BIOMES['field'], 500, {'Farmer': 1.0}, (LowerStrata(1000, 'Farmer'), )), 
         1000),
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(500, 'Farmer'), LowerStrata(500, 'Miner'))), 
         1000),
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1000, 'Farmer'), LowerStrata(500, 'Miner'))), 
         1500),
        (Extractor('grain', BIOMES['field'], 500, {'Farmer': 1.0}), 
         0),
    ])
    def test_get_total_workers(self, extractor: Extractor, expected: float):
        super().test_get_total_workers(extractor, expected)

    @parameterized.expand([
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1000, 'Farmer'), )),
         {'Farmer': 1.0, 'Miner': 0.0}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(500, 'Farmer'), LowerStrata(500, 'Miner'))),
         {'Farmer': 0.5, 'Miner': 0.5}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(700, 'Farmer'), LowerStrata(300, 'Miner'))),
         {'Farmer': 0.7, 'Miner': 0.3}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}),
         {'Farmer': 0.5, 'Miner': 0.5}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1000, 'Farmer'), LowerStrata(500, 'Miner'))),
         {'Farmer': 2/3, 'Miner': 1/3}),
    ])
    def test_get_real_proportion(self, extractor: Extractor, expected: dict[str, float]) -> None:
        super().test_get_real_proportion(extractor, expected)

    @parameterized.expand([
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(1000, 'Farmer'), )), 
         {}),

        (Extractor('grain', BIOMES['hill'],  1000, {'Farmer': 1.0}, (LowerStrata(1000, 'Farmer'), )),
         {}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )),
         {'Farmer': 500}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(1500, 'Farmer'), )),
         {}),

        ################
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1000, 'Farmer'), )),
         {}),

        (Extractor('grain', BIOMES['field'], 1500, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1000, 'Farmer'), )),
         {'Miner': 500}),

        (Extractor('grain', BIOMES['field'], 3000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1000, 'Farmer'), )),
         {'Farmer': 500, 'Miner': 1500}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1/3, 'Miner': 1/3, 'Laborer': 1/3}, (LowerStrata(200, 'Farmer'), )),
         {'Farmer': 133 + 1/3, 'Miner': 333 + 1/3, 'Laborer': 333 + 1/3}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 4/6, 'Miner': 1/6, 'Laborer': 1/6}, (LowerStrata(800, 'Laborer'), )),
         {'Farmer': 160, 'Miner': 40}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 3/6, 'Miner': 1/6, 'Laborer': 2/6}, (LowerStrata(800, 'Laborer'), )),
         {'Farmer': 150, 'Miner': 50}),
    ])
    def test_get_labor_demand(self, extractor: Extractor, expected: dict[str, float]) -> None:
        super().test_get_labor_demand(extractor, expected)
    
    @parameterized.expand([
        ('just_farmer', (LowerStrata(500, 'Farmer'), ), {'Farmer': LowerStrata(1000, 'Farmer')}),
        ('just_farmer', (LowerStrata(100, 'Farmer'), ), {'Farmer': LowerStrata(600, 'Farmer')}),
        ('just_farmer', (LowerStrata(-250, 'Farmer'), ), {'Farmer': LowerStrata(250, 'Farmer')}),
        ('just_farmer', (LowerStrata(-500, 'Farmer'), ), {'Farmer': LowerStrata(0, 'Farmer')}),
        ('just_farmer', (LowerStrata(-1000, 'Farmer'), ), None),
        ('just_farmer', tuple(), {'Farmer': LowerStrata(500, 'Farmer')}),

        ('just_farmer', (LowerStrata(500, 'Miner'), ), None),
        ('just_farmer', (LowerStrata(1000, 'Miner'), ), None),
        ('just_farmer', (LowerStrata(-500, 'Miner'), ), None),
        ('just_farmer', (LowerStrata(-1000, 'Miner'), ), None),

        ('farmer_miner', (LowerStrata(500, 'Farmer'), ), {'Farmer': LowerStrata(750, 'Farmer'), 'Miner': LowerStrata(250, 'Miner')}),
        ('farmer_miner', (LowerStrata(1000, 'Farmer'), ), {'Farmer': LowerStrata(1250, 'Farmer'), 'Miner': LowerStrata(250, 'Miner')}),
        ('farmer_miner', (LowerStrata(250, 'Farmer'), LowerStrata(250, 'Miner'), ), {'Farmer': LowerStrata(500, 'Farmer'), 'Miner': LowerStrata(500, 'Miner')}),
        ('farmer_miner', (LowerStrata(500, 'Farmer'), LowerStrata(500, 'Miner'), ), {'Farmer': LowerStrata(750, 'Farmer'), 'Miner': LowerStrata(750, 'Miner')}),
        ('farmer_miner', (LowerStrata(-250, 'Farmer'), LowerStrata(250, 'Miner'), ), {'Farmer': LowerStrata(0, 'Farmer'), 'Miner': LowerStrata(500, 'Miner')}),
        ('farmer_miner', (LowerStrata(-500, 'Farmer'), LowerStrata(250, 'Miner'), ), None),
        ('farmer_miner', tuple(), {'Farmer': LowerStrata(250, 'Farmer'), 'Miner': LowerStrata(250, 'Miner')}),
    ])
    def test_distribute_workers(self, industry: str, workers: tuple[Population, ...], expected: dict[str, float] | None) -> None:
        super().test_distribute_workers(industry, workers, expected)

    @parameterized.expand([
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )),
         {}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(500, 'Farmer'), )),
         {'Miner': 500}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1/3, 'Miner': 1/3, 'Laborer': 1/3}, (LowerStrata(500, 'Farmer'), )),
         {'Miner': 500, 'Laborer': 500}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1/3, 'Miner': 1/3, 'Laborer': 1/3}, (LowerStrata(500, 'Farmer'), LowerStrata(200, 'Miner'))),
         {'Miner': 500, 'Laborer': 500}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1/3, 'Miner': 1/3, 'Laborer': 1/3}, (LowerStrata(200, 'Farmer'), LowerStrata(200, 'Miner'))),
         {'Laborer': 200}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 4/6, 'Miner': 1/6, 'Laborer': 1/6}, (LowerStrata(800, 'Laborer'), )),
         {'Farmer': 3200, 'Miner': 800}),
    ])
    def test_get_correct_sizes(self, extractor: Extractor, expected: dict[str, float]):
        super().test_get_correct_sizes(extractor, expected)

    @parameterized.expand([
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )), 
         {}),
         
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(500, 'Farmer'), )), 
         {'Miner': 500}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(500, 'Miner'), )), 
         {'Farmer': 500}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(200, 'Farmer'), LowerStrata(300, 'Miner'))), 
         {'Farmer': 100}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, (LowerStrata(1100, 'Farmer'), LowerStrata(1200, 'Miner'))), 
         {}),

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1/3, 'Miner': 1/3, 'Laborer': 1/3}, (LowerStrata(100, 'Farmer'), LowerStrata(200, 'Miner'), LowerStrata(100, 'Laborer'))), 
         {'Farmer': 100, 'Laborer': 100}),  # Current 25%, 50%, 25%
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 4/6, 'Miner': 1/6, 'Laborer': 1/6}, (LowerStrata(800, 'Laborer'), )),
         {'Farmer': 160, 'Miner': 40}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 3/6, 'Miner': 1/6, 'Laborer': 2/6}, (LowerStrata(800, 'Laborer'), )),
         {'Farmer': 150, 'Miner': 50}),
    ])
    def test_get_fix_proportion(self, extractor: Extractor, expected: dict[str, float]) -> None:
        super().test_get_fix_proportion(extractor, expected)

    @parameterized.expand([
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )), 
         6000),  # 500 * 1.2 * 10 * 1.0
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(1000, 'Farmer'), )), 
         12000),  # 500 * 1.2 * 10 * 1.0
        (Extractor('grain', BIOMES['hill'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )), 
         3000),  # 500 * .6 * 10 * 1.0
        (Extractor('grain', BIOMES['hill'], 1000, {'Farmer': 1.0}, (LowerStrata(1000, 'Farmer'), )), 
         6000),  # 500 * .6 * 10 * 1.0

        (Extractor('iron', BIOMES['field'], 1000, {'Miner': 1.0}, (LowerStrata(500, 'Miner'), )), 
         1000),  # 500 * 1.0 * 2 * 1.0
        (Extractor('iron', BIOMES['field'], 1000, {'Miner': 1.0}, (LowerStrata(1000, 'Miner'), )), 
         2000),  # 500 * 1.0 * 2 * 1.0
        (Extractor('iron', BIOMES['hill'], 1000, {'Miner': 1.0}, (LowerStrata(500, 'Miner'), )), 
         1100),  # 500 * 1.1 * 2 * 1.0
        (Extractor('iron', BIOMES['hill'], 1000, {'Miner': 1.0}, (LowerStrata(1000, 'Miner'), )), 
         2200),  # 500 * 1.1 * 2 * 1.0

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Laborer': 0.5}, (LowerStrata(250, 'Farmer'), LowerStrata(250, 'Laborer'), )), 
         6000),  # 500 * 1.2 * 10 * 1.0
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Laborer': 0.5}, (LowerStrata(500, 'Farmer'), LowerStrata(500, 'Laborer'), )), 
         12000),  # 500 * 1.2 * 10 * 1.0
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Laborer': 0.5}, (LowerStrata(250, 'Farmer'), LowerStrata(100, 'Laborer'), )), 
         2399.99999999999999),  # 350 * 1.2 * 10 * 0.57142857
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.8, 'Laborer': 0.2}, (LowerStrata(250, 'Farmer'), LowerStrata(250, 'Laborer'), )), 
         2400),  # 500 * 1.2 * 10 * 0.4
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Laborer': 0.5}, (LowerStrata(500, 'Farmer'), )), 
         0),  # 500 * 1.2 * 10 * 0
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Laborer': 0.5}, (LowerStrata(500, 'Laborer'), )), 
         0),  # 500 * 1.2 * 10 * 0
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.4, 'Laborer': 0.6}, (LowerStrata(500, 'Farmer'), )), 
         0),  # 500 * 1.2 * 10 * 0.0 (-0.2)
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.6, 'Laborer': 0.4}, (LowerStrata(500, 'Farmer'), )), 
         1200),  # 500 * 1.2 * 10 * 0.2
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.9, 'Laborer': 0.1}, (LowerStrata(500, 'Farmer'), )), 
         4800.0),  # 500 * 1.2 * 10 * 0.8
    ])
    def test_get_production(self, extractor: Extractor, expected: float):
        super().test_get_production(extractor, expected)

    @parameterized.expand([
        # lower: self.needs = {'grain': 1}
        # middle: self.needs = {'grain': 2, 'iron': 1}
        # upper: self.needs = {'grain': 6, 'iron': 3}

        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )), {'grain': 500}),
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, 
                   (LowerStrata(500, 'Farmer'), LowerStrata(500, 'Miner'))), {'grain': 1000}),
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Miner': 0.5}, 
                   (LowerStrata(500, 'Farmer'), LowerStrata(1000, 'Miner'))), {'grain': 1500}),
        
        (Extractor('grain', BIOMES['field'], 1000, {'Farmer': 0.5, 'Bureaucrat': 0.5}, 
                   (LowerStrata(500, 'Farmer'), MiddleStrata(500, 'Bureaucrat'))), {'grain': 1500, 'iron': 500}),
        (Extractor('grain', BIOMES['field'], 1500, {'Farmer': 1/3, 'Bureaucrat': 1/3, 'Capitalist': 1/3}, 
                   (LowerStrata(500, 'Farmer'), MiddleStrata(500, 'Bureaucrat'), UpperStrata(500, 'Capitalist'))),
                    {'grain': 4500, 'iron': 2000}),
        (Extractor('grain', BIOMES['field'], 500, {'Farmer': 1/3, 'Bureaucrat': 1/3, 'Capitalist': 1/3}, 
                   (LowerStrata(500, 'Farmer'), MiddleStrata(500, 'Bureaucrat'), UpperStrata(500, 'Capitalist'))),
                    {'grain': 4500, 'iron': 2000}),
        (Extractor('grain', BIOMES['field'], 1500, {'Farmer': 1/3, 'Bureaucrat': 1/3, 'Capitalist': 1/3}, 
                   (LowerStrata(500, 'Farmer'), MiddleStrata(500, 'Bureaucrat'), UpperStrata(500, 'Capitalist'))),
                    {'grain': 500}, v.Strata.LOWER),
    ])
    def test_get_goods_demand(self, extractor: Extractor, expected: dict[str, float], stratum: Optional[v.Strata] = None) -> None:
        super().test_get_goods_demand(extractor, expected, stratum)

if __name__ == '__main__':
    system('cls')
    main()
