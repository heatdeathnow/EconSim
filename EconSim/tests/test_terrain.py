from sys import path
from os.path import join, dirname, abspath
from os import system

main_module_path = abspath(join(dirname(__file__), '..'))
path.insert(0, main_module_path)

import variables as v
v.TESTING = True
###########################################################################################################################################

from unittest import TestCase, main, skip
from parameterized import parameterized
from abc import ABC
from production import Extractor
from terrain import *

field = v.BIOMES['field']
hill  = v.BIOMES['hill']

class TestBiome(TestCase):

    @parameterized.expand([
        ('plains', {'grain': 1.1, 'iron': 1.0}, True),
        ('plains', {'iron': 1.0}, True),
        ('plains', {'XXX': 1.0}, False),
        ('plains', {'grain': 0.5, 'XXX': 1.0}, False),
    ])
    def test_good_dont_exist(self, name: str, adv: dict[str, float], expected: bool):
        if expected:
            try:
                Biome(name, **adv)
            
            except ValueError:
                self.fail()
            
        else:
            try:
                Biome(name, **adv)
                self.fail()
            
            except ValueError:
                pass

class TestProvince(TestCase):
    # def setUp(self) -> None:
        
    #     self.empty_field_grain = Province('Empty Field Grain', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0})})
    #     self.empty_field_iron = Province('Empty Field Iron', field, {'iron': Extractor('iron', field, 1000, {'Miner': 1.0})})

    #     self.empty_hill_grain = Province('Empty Hill Grain', hill, {'grain': Extractor('grain', hill, 1000, {'Farmer': 1.0})})
    #     self.empty_hill_iron = Province('Empty Hill Iron', hill, {'iron': Extractor('iron', hill, 1000, {'Miner': 1.0})})
        
    #     self.field_grain = Province('Field Grain', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), ))})
    #     self.field_iron = Province('Field Iron', field, {'iron': Extractor('iron', field, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Miner'), ))})

    #     self.hill_grain = Province('Hill Grain', hill, {'grain': Extractor('grain', hill, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), ))})
    #     self.hill_iron = Province('Hill Iron', hill, {'iron': Extractor('iron', hill, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Miner'), ))})

    #     self.both_field = Province('Both Field', field, 
    #                                {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )), 
    #                                 'iron' : Extractor('iron',  field, 1000, {'Miner': 1.0},  (LowerStrata(500, 'Miner'), ))})

    #     self.both_hill = Province('Both Field', hill, 
    #                                {'grain': Extractor('grain', hill, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )), 
    #                                 'iron' : Extractor('iron',  hill, 1000, {'Miner': 1.0},  (LowerStrata(500, 'Miner'), ))})

    # def tearDown(self) -> None:
    #     del self.empty_field_grain
    #     del self.empty_field_iron
    #     del self.empty_hill_grain
    #     del self.empty_hill_iron
    #     del self.field_grain
    #     del self.field_iron
    #     del self.hill_grain
    #     del self.hill_iron
    #     del self.both_field
    #     del self.both_hill
    
    @parameterized.expand([
        (Province('', field, {}, {}, LowerStrata(500)), None, 500),
        (Province('', field, {}, {}, LowerStrata(0)), None, 0),
        (Province('', field, {}, {}, LowerStrata(500),  MiddleStrata(300)), None, 800),
        (Province('', field, {}, {}, LowerStrata(500),  MiddleStrata(300)), 'lower', 500),
        (Province('', field, {}, {}, LowerStrata(500),  MiddleStrata(300)), 'middle', 300),
        (Province('', field, {}, {}, LowerStrata(500),  MiddleStrata(300)), 'upper', 0),
    ])
    def test_get_total_idle_pops(self, prov: Province, strata: Literal['lower', 'middle', 'upper', None], expected: int | None):
        idle_pops = prov.get_total_idle_pops(strata)
        self.assertEqual(idle_pops, expected)

    @parameterized.expand([
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), ))}, {}), {'Farmer': 500}),
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 0.5 , 'Miner': 0.5}, (LowerStrata(500, 'Farmer'), ))}, {}), {'Miner': 500}),
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 0.5 , 'Miner': 0.5}, (LowerStrata(400, 'Farmer'), ))}, {}), {'Farmer': 100, 'Miner': 500}),
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 0.2 , 'Miner': 0.8}, (LowerStrata(400, 'Farmer'), ))}, {}), {'Miner': 600}),
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 0.1 , 'Miner': 0.9}, (LowerStrata(50, 'Farmer'), ))}, {}), {'Farmer': 50, 'Miner': 900}),
    ])
    def test_get_total_labor_demand(self, prov: Province, expected: dict[str, int | float]):
        labor_demand = prov.get_total_labor_demand()
        for (key, val), (key_, val_) in zip(labor_demand.items(), expected.items()):
            self.assertEqual(key, key_)
            self.assertAlmostEqual(val, val_)

        self.assertEqual(labor_demand, expected)

    @parameterized.expand([
# Advantages
#   field: grain = 1.2; iron = 1.0
#   hill:  grain = 0.6; iron = 1.1
# 
# throughput
#   grain = 10, iron = 2

# 500 * 10 * 1.2 = 6000
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), ))}, {}), {'grain': 6000}),

# 500 * 2 * 1.1 = 1100
(Province('', field, {'iron': Extractor('iron', field, 1000, {'Miner': 1.0}, (LowerStrata(500, 'Miner'), ))}, {}), {'iron': 1000}),

(Province('', field,
          {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}, (LowerStrata(500, 'Farmer'), )),
           'iron':  Extractor('iron',  field, 1000, {'Miner': 1.0},  (LowerStrata(500, 'Miner'), ))}, 
           {}), {'grain': 6000, 'iron': 1000}),

    ])
    def test_get_output(self, prov: Province, expected: dict[str, float | int]):
        production = prov.get_output()

        for (key, val), (key_, val_) in zip(production.items(), expected.items()):
            self.assertEqual(key, key_)
            self.assertAlmostEqual(val, val_)
    
    @parameterized.expand([
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0})}, {}, LowerStrata(500)), ({'Farmer': 500} ,)),
(Province('', field, {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0})}, {}, LowerStrata(2000)), ({'Farmer': 1000} ,)),

(Province('', field, 
          {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}), 'iron' : Extractor('grain', field, 1000, {'Miner': 1.0})}, 
          {}, LowerStrata(500)), ({'Farmer': 250}, {'Miner': 250})),
(Province('', field, 
          {'grain': Extractor('grain', field, 1000, {'Farmer': 1.0}), 'iron' : Extractor('grain', field, 1000, {'Miner': 1.0})}, 
          {}, LowerStrata(3000)), ({'Farmer': 1000}, {'Miner': 1000})),

(Province('', field,
          {'grain': Extractor('grain', field, 1000, {'Farmer': 0.8, 'Miner': 0.2})}, 
          {}, LowerStrata(500)), ({'Farmer': 400, 'Miner': 100},)),
(Province('', field, 
          {'grain': Extractor('grain', field, 1000, {'Farmer': 0.8, 'Miner': 0.2})}, 
          {}, LowerStrata(2000)), ({'Farmer': 800, 'Miner': 200},)),

(Province('', field,
          {'grain': Extractor('grain', field, 1000, {'Farmer': 0.8, 'Miner': 0.2}),
           'iron' : Extractor('grain', field, 1000, {'Farmer': 0.5, 'Miner': 0.5})}, 
          {}, LowerStrata(500)), ({'Farmer': 200, 'Miner': 50}, {'Farmer': 125, 'Miner': 125})),
(Province('', field,
          {'grain': Extractor('grain', field, 1000, {'Farmer': 0.8, 'Miner': 0.2}),
           'iron' : Extractor('grain', field, 1000, {'Farmer': 0.5, 'Miner': 0.5})}, 
          {}, LowerStrata(3000)), ({'Farmer': 800, 'Miner': 200}, {'Farmer': 500, 'Miner': 500})),

    ])
    def test_distribute_idle_pops(self, prov: Province, expected: tuple[dict[str, float | int]]):
        prov.distribute_idle_pops()

        self.assertEqual(len(prov.industries), len(expected))
        for industry, exp in zip(prov.industries.values(), expected):
            for (r_occupation, r_population), (e_occupation, e_size) in zip(industry.workers.items(), exp.items()):
                self.assertEqual(r_occupation, e_occupation)
                self.assertAlmostEqual(r_population.size, e_size)

if __name__ == '__main__':
    system('cls')
    main()
