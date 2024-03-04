from abc import ABC
from decimal import getcontext
from pathlib import Path
from importlib import import_module
from unittest import TestCase, TestLoader, TextTestRunner
from source import Q
from source.abcs import Dyct
from source.algs import balance_alg, sharing_alg
from source.goods import Good, ProdTech, Products, Stock
from source.pop import Commune, Pop
from source.prod import Extractor, Industry, Manufactury

Q = Q * 10

class PopMixIn(ABC, TestCase):
    def assert_pops_equal(self, pop1: Pop, pop2: Pop):
        self.assertEqual(pop1.stratum, pop2.stratum)
        self.assertEqual(pop1.job, pop2.job)
        self.assertAlmostEqual(pop1.size, pop2.size, delta=Q)
        self.assertAlmostEqual(pop1.welfare, pop2.welfare, delta=Q)

    def assert_communes_equal(self, com1: Commune, com2: Commune):
        self.assertEqual(len(com1), len(com2))

        for key, pop in com1.items():
            self.assert_pops_equal(pop, com2[key])

class GoodsMixIn(ABC, TestCase):
    def assert_goods_equal(self, good1: Good, good2: Good):
        self.assertEqual(good1.product, good2.product)
        self.assertEqual(good1.name, good2.name)
        self.assertAlmostEqual(good1.amount, good2.amount, delta=Q)
    
    def assert_stocks_equal(self, stock1: Stock | Dyct[Products, Good], stock2: Stock | Dyct[Products, Good]):
        self.assertEqual(len(stock1), len(stock2))
        for product, good in stock1.items():
            self.assert_goods_equal(good, stock2[product])

class ProdMixIn(PopMixIn, GoodsMixIn):

    def assert_industries_equal(self, ind1: Industry, ind2: Industry):
        self.assertIs(type(ind1), type(ind2))
        self.assertEqual(ind1.product, ind2.product)
        self.assertEqual(ind1.prod_tech, ind2.prod_tech)
        self.assertDictEqual(ind1.needed_workers, ind2.needed_workers)
        self.assert_communes_equal(ind1.workforce, ind2.workforce)

        if isinstance(ind1, Manufactury):
            self.assertNotEqual(ind1.prod_tech, ProdTech.EXTRACTION)
            self.assert_stocks_equal(ind1.stockpile, ind2.stockpile)  # type: ignore

class AlgsMixIn(ProdMixIn):

    def assert_shares_correctly(self, sharing_alg: sharing_alg, com: Commune, stock: Stock, com_exp: Commune, stock_exp: Stock):
        sharing_alg(com, stock)
        self.assert_communes_equal(com, com_exp)
        self.assert_stocks_equal(stock, stock_exp)
    
    def assert_balances_correctly(self, balancing_alg: balance_alg, ext: Extractor, com_exp: Commune, ext_exp: Extractor):
        unemployed = ext.balance(balancing_alg)
        self.assert_communes_equal(unemployed, com_exp)
        self.assert_industries_equal(ext, ext_exp)

####################################################################################################################################

loader = TestLoader()
runner = TextTestRunner()
tests_path = (Path.cwd() / __file__).parent

for directory in tests_path.iterdir():
    if not directory.is_dir() and not directory.name.startswith('__'):

        module_name = f'{tests_path.name}.{directory.with_suffix('').name}'
        
        # ['tests.test_goods', 'tests.test_pop', 'tests.test_prod', 'tests.test_algs', ]
        if module_name in ['tests.test_goods', 'tests.test_pop', 'tests.test_algs', ]: continue

        module = import_module(module_name)

        print(f'\n\nRunning tests for {directory.name}...')
        suite = loader.loadTestsFromModule(module)

        runner.run(suite)
