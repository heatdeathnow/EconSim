from sys import path
from os.path import join, dirname, abspath
from os import system

main_module_path = abspath(join(dirname(__file__), '..'))
path.insert(0, main_module_path)

###########################################################################################################################################

from unittest import TestCase, main
from parameterized import parameterized
from abc import ABC
from population import *

class PopulationTest(ABC):

    @abstractmethod
    def test_get_consumption(self, expected: dict[str, int]) -> None:
        for pop in self.pops.values():
            consumption = pop.get_consumption()

            self.assertEqual(consumption, expected)

    @abstractmethod
    def test_get_welfare(self, stockpile: dict[str, int], expected: float) -> None:
        for pop in self.pops.values():
            consumption = pop.get_consumption()
            welfare = pop.get_welfare(stockpile, consumption)

            self.assertAlmostEqual(welfare, expected)

    @abstractmethod
    def test_get_change(self, occupation: str, welfare: float, expected: tuple[Population, ...]) -> None:
        self.pops: dict[str, Population]
        change = self.pops[occupation].get_change(welfare)

        self.assertEqual(change, expected)

    @abstractmethod
    def test_add(self, occupation: str, value: Population | int | float, expected: Population | None):
        try:
            addition = self.pops[occupation] + value
            self.assertEqual(addition, expected)
        
        except TypeError:
            if expected is None:
                pass

            else:
                self.fail()
    
    @abstractmethod
    def test_radd(self, occupation: str, value: Population | int | float, expected: Population | None):
        try:
            addition = value + self.pops[occupation]
            self.assertEqual(addition, expected)
        
        except TypeError:
            if expected is None:
                pass

            else:
                self.fail()
    
    @abstractmethod
    def test_iadd(self, occupation: str, value: Population | int | float, expected: Population | None):
        try:
            self.pops[occupation] += value
            self.assertEqual(self.pops[occupation], expected)
        
        except TypeError:
            if expected is None:
                pass

            else:
                self.fail()

    @abstractmethod
    def test_sub(self, occupation: str, value: Population | int | float, expected: Population | None):
        try:
            subtraction = self.pops[occupation] - value
            self.assertEqual(subtraction, expected)
        
        except TypeError:
            if expected is None:
                pass

            else:
                self.fail()
    
    @abstractmethod
    def test_rsub(self, occupation: str, value: Population | int | float, expected: Population | None):
        try:
            subtraction = value - self.pops[occupation]
            self.assertEqual(subtraction, expected)
        
        except TypeError:
            if expected is None:
                pass

            else:
                self.fail()
    
    @abstractmethod
    def test_isub(self, occupation: str, value: Population | int | float, expected: Population | None):
        try:
            self.pops[occupation] -= value
            self.assertEqual(self.pops[occupation], expected)
        
        except TypeError:
            if expected is None:
                pass

            else:
                self.fail()

class UpperStrataTest(TestCase, PopulationTest):

    OPER_PARAMS_POS_LEFT = [
        # Additions of stratas of the same subclass.
        ('Capitalist', UpperStrata(10, 'Capitalist'), UpperStrata(1010, 'Capitalist')),
        ('Capitalist', UpperStrata(0, 'Capitalist'), UpperStrata(1000, 'Capitalist')),
        ('Capitalist', UpperStrata(-10, 'Capitalist'), UpperStrata(990, 'Capitalist')),
        ('Capitalist', UpperStrata(1.1, 'Capitalist'), UpperStrata(1001.1, 'Capitalist')),

        # Addition of strata of the same subclass but different occupations.
        ('Capitalist', UpperStrata(10, 'Official'), None),
        ('Capitalist', UpperStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Capitalist', MiddleStrata(10, 'Artisan'), None),
        ('Capitalist', LowerStrata(10, 'Farmer'), None),

        # Addition with ints and floats
        ('Capitalist', 10, UpperStrata(1010, 'Capitalist')),
        ('Capitalist', 0, UpperStrata(1000, 'Capitalist')),
        ('Capitalist', -10, UpperStrata(990, 'Capitalist')),
        ('Capitalist', 1.1, UpperStrata(1001.1, 'Capitalist')),
    ]

    OPER_PARAMS_NEG_LEFT = [
        # Additions of stratas of the same subclass.
        ('Capitalist', UpperStrata(10, 'Capitalist'), UpperStrata(990, 'Capitalist')),
        ('Capitalist', UpperStrata(0, 'Capitalist'), UpperStrata(1000, 'Capitalist')),
        ('Capitalist', UpperStrata(-10, 'Capitalist'), UpperStrata(1010, 'Capitalist')),
        ('Capitalist', UpperStrata(1.1, 'Capitalist'), UpperStrata(998.9, 'Capitalist')),

        # Addition of strata of the same subclass but different occupations.
        ('Capitalist', UpperStrata(10, 'Official'), None),
        ('Capitalist', UpperStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Capitalist', MiddleStrata(10, 'Artisan'), None),
        ('Capitalist', LowerStrata(10, 'Farmer'), None),

        # Addition with ints and floats
        ('Capitalist', 10, UpperStrata(990, 'Capitalist')),
        ('Capitalist', 0, UpperStrata(1000, 'Capitalist')),
        ('Capitalist', -10, UpperStrata(1010, 'Capitalist')),
        ('Capitalist', 1.1, UpperStrata(998.9, 'Capitalist')),
    ]

    OPER_PARAMS_NEG_RIGHT = [
        # Additions of stratas of the same subclass.
        ('Capitalist', UpperStrata(10, 'Capitalist'), UpperStrata(-990, 'Capitalist')),
        ('Capitalist', UpperStrata(0, 'Capitalist'), UpperStrata(-1000, 'Capitalist')),
        ('Capitalist', UpperStrata(-10, 'Capitalist'), UpperStrata(-1010, 'Capitalist')),
        ('Capitalist', UpperStrata(1.1, 'Capitalist'), UpperStrata(-998.9, 'Capitalist')),

        # Addition of strata of the same subclass but different occupations.
        ('Capitalist', UpperStrata(10, 'Official'), None),
        ('Capitalist', UpperStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Capitalist', MiddleStrata(10, 'Artisan'), None),
        ('Capitalist', LowerStrata(10, 'Farmer'), None),

        # Addition with ints and floats
        ('Capitalist', 10, UpperStrata(-990, 'Capitalist')),
        ('Capitalist', 0, UpperStrata(-1000, 'Capitalist')),
        ('Capitalist', -10, UpperStrata(-1010, 'Capitalist')),
        ('Capitalist', 1.1, UpperStrata(-998.9, 'Capitalist')),
    ]

    def setUp(self) -> None:
        self.pops = {
                'Capitalist': UpperStrata(1000, 'Capitalist'),
                'Official': UpperStrata(1000, 'Official'),
                'Idle': UpperStrata(1000)
            }
    
    def tearDown(self) -> None:
        del self.pops

    def test_get_consumption(self) -> None:
        super().test_get_consumption({'grain': 6000, 'iron': 3000})

    @parameterized.expand([
        # Needs fully fulfilled.
        ({'grain': 999999, 'iron': 999999}, 1.0),  # self.needs = {'grain': 6, 'iron': 3}

        # Needs completely unfulfilled.
        ({'grain': 0, 'iron': 0}, 0.0),

        # Needs halfway fulfilled.
        ({'grain': 3000, 'iron': 1500}, 0.5),

        # Needs fulfilled in non-equal amounts
        ({'grain': 1500, 'iron': 900}, 0.275),  # ((1500 / 6000) + (900 / 3000)) / 2

        # One has more than enough, the other not.
        ({'grain': 1500, 'iron': 3100}, 0.625),  # ((1500 / 6000) + (3000 / 3000)) / 2
    ])
    def test_get_welfare(self, stockpile: dict[str, int], expected: float) -> None:
        super().test_get_welfare(stockpile, expected)

    @parameterized.expand([
        ('Capitalist', 1.0, (UpperStrata(10, 'Capitalist'), )),  # self.growth_rate = 0.01
        ('Official', 1.0, (UpperStrata(10, 'Official'), )),
        ('Idle', 1.0, (UpperStrata(10, None), )),

        ('Capitalist', 0.0, (MiddleStrata(50, None), )),  # self.demotion_rate = 0.05
        ('Official', 0.0, (MiddleStrata(50, None), )),
        ('Idle', 0.0, (MiddleStrata(50, None), )),
    ])
    def test_get_change(self, occupation: str, welfare: float, expected: tuple[Population, ...]) -> None:
        super().test_get_change(occupation, welfare, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_add(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_add(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_radd(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_radd(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_iadd(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_iadd(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_LEFT)
    def test_sub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_sub(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_RIGHT)
    def test_rsub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_rsub(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_LEFT)
    def test_isub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_isub(occupation, value, expected)

class MiddleStrataTest(TestCase, PopulationTest):

    OPER_PARAMS_POS_LEFT = [
        # Additions of stratas of the same subclass.
        ('Artisan', MiddleStrata(10, 'Artisan'), MiddleStrata(1010, 'Artisan')),
        ('Artisan', MiddleStrata(0, 'Artisan'), MiddleStrata(1000, 'Artisan')),
        ('Artisan', MiddleStrata(-10, 'Artisan'), MiddleStrata(990, 'Artisan')),
        ('Artisan', MiddleStrata(1.1, 'Artisan'), MiddleStrata(1001.1, 'Artisan')),

        # Addition of strata of the same subclass but different occupations.
        ('Artisan', MiddleStrata(10, 'Bureaucrat'), None),
        ('Artisan', MiddleStrata(10, 'Specialist'), None),
        ('Artisan', MiddleStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Artisan', LowerStrata(10, 'Farmer'), None),
        ('Artisan', UpperStrata(10, 'Capitalist'), None),

        # Addition with ints and floats
        ('Artisan', 10, MiddleStrata(1010, 'Artisan')),
        ('Artisan', 0, MiddleStrata(1000, 'Artisan')),
        ('Artisan', -10, MiddleStrata(990, 'Artisan')),
        ('Artisan', 1.1, MiddleStrata(1001.1, 'Artisan')),
    ]

    OPER_PARAMS_NEG_LEFT = [
        # Additions of stratas of the same subclass.
        ('Artisan', MiddleStrata(10, 'Artisan'), MiddleStrata(990, 'Artisan')),
        ('Artisan', MiddleStrata(0, 'Artisan'), MiddleStrata(1000, 'Artisan')),
        ('Artisan', MiddleStrata(-10, 'Artisan'), MiddleStrata(1010, 'Artisan')),
        ('Artisan', MiddleStrata(1.1, 'Artisan'), MiddleStrata(998.9, 'Artisan')),

        # Addition of strata of the same subclass but different occupations.
        ('Artisan', MiddleStrata(10, 'Bureaucrat'), None),
        ('Artisan', MiddleStrata(10, 'Specialist'), None),
        ('Artisan', MiddleStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Artisan', LowerStrata(10, 'Farmer'), None),
        ('Artisan', UpperStrata(10, 'Capitalist'), None),

        # Addition with ints and floats
        ('Artisan', 10, MiddleStrata(990, 'Artisan')),
        ('Artisan', 0, MiddleStrata(1000, 'Artisan')),
        ('Artisan', -10, MiddleStrata(1010, 'Artisan')),
        ('Artisan', 1.1, MiddleStrata(998.9, 'Artisan')),
    ]

    OPER_PARAMS_NEG_RIGHT = [
        # Additions of stratas of the same subclass.
        ('Artisan', MiddleStrata(10, 'Artisan'), MiddleStrata(-990, 'Artisan')),
        ('Artisan', MiddleStrata(0, 'Artisan'), MiddleStrata(-1000, 'Artisan')),
        ('Artisan', MiddleStrata(-10, 'Artisan'), MiddleStrata(-1010, 'Artisan')),
        ('Artisan', MiddleStrata(1.1, 'Artisan'), MiddleStrata(-998.9, 'Artisan')),

        # Addition of strata of the same subclass but different occupations.
        ('Artisan', MiddleStrata(10, 'Bureaucrat'), None),
        ('Artisan', MiddleStrata(10, 'Specialist'), None),
        ('Artisan', MiddleStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Artisan', LowerStrata(10, 'Farmer'), None),
        ('Artisan', UpperStrata(10, 'Capitalist'), None),

        # Addition with ints and floats
        ('Artisan', 10, MiddleStrata(-990, 'Artisan')),
        ('Artisan', 0, MiddleStrata(-1000, 'Artisan')),
        ('Artisan', -10, MiddleStrata(-1010, 'Artisan')),
        ('Artisan', 1.1, MiddleStrata(-998.9, 'Artisan')),
    ]

    def setUp(self) -> None:
        self.pops = {
            'Artisan': MiddleStrata(1000, 'Artisan'),
            'Bureaucrat': MiddleStrata(1000, 'Bureaucrat'),
            'Specialist': MiddleStrata(1000, 'Specialist'),
            'Idle': MiddleStrata(1000)
        }

    def tearDown(self) -> None:
        del self.pops

    def test_get_consumption(self) -> None:
        super().test_get_consumption({'grain': 2000, 'iron': 1000})

    @parameterized.expand([
        # Needs fully fulfilled.
        ({'grain': 999999, 'iron': 999999}, 1.0),  # self.needs = {'grain': 2, 'iron': 1}

        # Needs completely unfulfilled.
        ({'grain': 0, 'iron': 0}, 0.0),

        # Needs halfway fulfilled.
        ({'grain': 1000, 'iron': 500}, 0.5),

        # Needs fulfilled in non-equal amounts
        ({'grain': 1500, 'iron': 900}, 0.825),  # ((1500 / 2000) + (900 / 1000)) / 2

        # One has more than enough, the other not.
        ({'grain': 1500, 'iron': 3100}, 0.875),  # ((1500 / 2000) + (1000 / 1000)) / 2
    ])
    def test_get_welfare(self, stockpile: dict[str, int], expected: float) -> None:
        super().test_get_welfare(stockpile, expected)

    @parameterized.expand([
        # Enough to grow and promote
        ('Artisan', 1.0, (UpperStrata(10, None), MiddleStrata(30, 'Artisan'))),  # self.growth_rate = 0.03, self.promotion_rate = 0.01
        ('Bureaucrat', 1.0, (UpperStrata(10, None), MiddleStrata(30, 'Bureaucrat'))),
        ('Specialist', 1.0, (UpperStrata(10, None), MiddleStrata(30, 'Specialist'))),
        ('Idle', 1.0, (UpperStrata(10, None), MiddleStrata(30, None))),

        # Just enough to grow
        ('Artisan', 0.8, (MiddleStrata(30, 'Artisan'), )),
        ('Bureaucrat', 0.8, (MiddleStrata(30, 'Bureaucrat'), )),
        ('Specialist', 0.8, (MiddleStrata(30, 'Specialist'), )),
        ('Idle', 0.8, (MiddleStrata(30, None), )),

        # Low enough for decline
        ('Artisan', 0.0, (LowerStrata(30, None), )),  # self.demotion_rate = 0.03
        ('Bureaucrat', 0.0, (LowerStrata(30, None), )),
        ('Specialist', 0.0, (LowerStrata(30, None), )),
        ('Idle', 0.0, (LowerStrata(30, None), )),
    ])
    def test_get_change(self, occupation: str, welfare: float, expected: tuple[Population, ...]) -> None:
        super().test_get_change(occupation, welfare, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_add(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_add(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_radd(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_radd(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_iadd(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_iadd(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_LEFT)
    def test_sub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_sub(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_RIGHT)
    def test_rsub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_rsub(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_LEFT)
    def test_isub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_isub(occupation, value, expected)

class LowerStrataTest(TestCase, PopulationTest):

    OPER_PARAMS_POS_LEFT = [
        # Additions of stratas of the same subclass.
        ('Farmer', LowerStrata(10, 'Farmer'), LowerStrata(1010, 'Farmer')),
        ('Farmer', LowerStrata(0, 'Farmer'), LowerStrata(1000, 'Farmer')),
        ('Farmer', LowerStrata(-10, 'Farmer'), LowerStrata(990, 'Farmer')),
        ('Farmer', LowerStrata(1.1, 'Farmer'), LowerStrata(1001.1, 'Farmer')),

        # Addition of strata of the same subclass but different occupations.
        ('Farmer', LowerStrata(10, 'Miner'), None),
        ('Farmer', LowerStrata(10, 'Laborer'), None),
        ('Farmer', LowerStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Farmer', MiddleStrata(10, 'Artisan'), None),
        ('Farmer', UpperStrata(10, 'Capitalist'), None),

        # Addition with ints and floats
        ('Farmer', 10, LowerStrata(1010, 'Farmer')),
        ('Farmer', 0, LowerStrata(1000, 'Farmer')),
        ('Farmer', -10, LowerStrata(990, 'Farmer')),
        ('Farmer', 1.1, LowerStrata(1001.1, 'Farmer')),
    ]

    OPER_PARAMS_NEG_LEFT = [
        # Additions of stratas of the same subclass.
        ('Farmer', LowerStrata(10, 'Farmer'), LowerStrata(990, 'Farmer')),
        ('Farmer', LowerStrata(0, 'Farmer'), LowerStrata(1000, 'Farmer')),
        ('Farmer', LowerStrata(-10, 'Farmer'), LowerStrata(1010, 'Farmer')),
        ('Farmer', LowerStrata(1.1, 'Farmer'), LowerStrata(998.9, 'Farmer')),

        # Addition of strata of the same subclass but different occupations.
        ('Farmer', LowerStrata(10, 'Miner'), None),
        ('Farmer', LowerStrata(10, 'Laborer'), None),
        ('Farmer', LowerStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Farmer', MiddleStrata(10, 'Artisan'), None),
        ('Farmer', UpperStrata(10, 'Capitalist'), None),

        # Addition with ints and floats
        ('Farmer', 10, LowerStrata(990, 'Farmer')),
        ('Farmer', 0, LowerStrata(1000, 'Farmer')),
        ('Farmer', -10, LowerStrata(1010, 'Farmer')),
        ('Farmer', 1.1, LowerStrata(998.9, 'Farmer')),
    ]

    OPER_PARAMS_NEG_RIGHT = [
        # Additions of stratas of the same subclass.
        ('Farmer', LowerStrata(10, 'Farmer'), LowerStrata(-990, 'Farmer')),
        ('Farmer', LowerStrata(0, 'Farmer'), LowerStrata(-1000, 'Farmer')),
        ('Farmer', LowerStrata(-10, 'Farmer'), LowerStrata(-1010, 'Farmer')),
        ('Farmer', LowerStrata(1.1, 'Farmer'), LowerStrata(-998.9, 'Farmer')),

        # Addition of strata of the same subclass but different occupations.
        ('Farmer', LowerStrata(10, 'Miner'), None),
        ('Farmer', LowerStrata(10, 'Laborer'), None),
        ('Farmer', LowerStrata(10, None), None),
        
        # Addition of strata of different subclasses.
        ('Farmer', MiddleStrata(10, 'Artisan'), None),
        ('Farmer', UpperStrata(10, 'Capitalist'), None),

        # Addition with ints and floats
        ('Farmer', 10, LowerStrata(-990, 'Farmer')),
        ('Farmer', 0, LowerStrata(-1000, 'Farmer')),
        ('Farmer', -10, LowerStrata(-1010, 'Farmer')),
        ('Farmer', 1.1, LowerStrata(-998.9, 'Farmer')),
    ]

    def setUp(self) -> None:
        self.pops = {
            'Farmer': LowerStrata(1000, 'Farmer'),
            'Miner': LowerStrata(1000, 'Miner'),
            'Laborer': LowerStrata(1000, 'Laborer'),
            'Idle': LowerStrata(1000),
        }

    def tearDown(self) -> None:
        del self.pops

    def test_get_consumption(self) -> None:
        super().test_get_consumption({'grain': 1000})

    @parameterized.expand([
        # Needs fully fulfilled.
        ({'grain': 999999}, 1.0),  # self.needs = {'grain': 1}

        # Needs completely unfulfilled.
        ({'grain': 0}, 0.0),

        # Needs halfway fulfilled.
        ({'grain': 500}, 0.5),

        # One has more than enough, the other not.
        ({'grain': 300}, 0.3),  # ((300 / 1000) / 1
    ])
    def test_get_welfare(self, stockpile: dict[str, int], expected: float) -> None:
        super().test_get_welfare(stockpile, expected)

    @parameterized.expand([
        # Enough to grow and promote
        ('Farmer', 1.0, (MiddleStrata(30, None), LowerStrata(50, 'Farmer'))),  # self.growth_rate = 0.05, self.promotion_rate = 0.03
        ('Miner', 1.0, (MiddleStrata(30, None), LowerStrata(50, 'Miner'))),
        ('Laborer', 1.0, (MiddleStrata(30, None), LowerStrata(50, 'Laborer'))),
        ('Idle', 1.0, (MiddleStrata(30, None), LowerStrata(50, None))),

        # Just enough to grow
        ('Farmer', 0.8, (LowerStrata(50, 'Farmer'), )),
        ('Miner', 0.8, (LowerStrata(50, 'Miner'), )),
        ('Laborer', 0.8, (LowerStrata(50, 'Laborer'), )),
        ('Idle', 0.8, (LowerStrata(50, None), )),

        # Low enough for decline
        ('Farmer', 0.0, (LowerStrata(-10, 'Farmer'), )),  # self.decline_rate = 0.01
        ('Miner', 0.0, (LowerStrata(-10, 'Miner'), )),
        ('Laborer', 0.0, (LowerStrata(-10, 'Laborer'), )),
        ('Idle', 0.0, (LowerStrata(-10, None), )),
    ])
    def test_get_change(self, occupation: str, welfare: float, expected: tuple[Population, ...]) -> None:
        super().test_get_change(occupation, welfare, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_add(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_add(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_radd(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_radd(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_POS_LEFT)
    def test_iadd(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_iadd(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_LEFT)
    def test_sub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_sub(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_RIGHT)
    def test_rsub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_rsub(occupation, value, expected)

    @parameterized.expand(OPER_PARAMS_NEG_LEFT)
    def test_isub(self, occupation: str, value: Population | int | float, expected: Population | int | float | Exception):
        super().test_isub(occupation, value, expected)

if __name__ == '__main__':
    system('cls')
    main()
