1. Population sizes now are set to zero to sizes close to one one-thousandth.
2. Added `is_balanced` and `balance` methods to the `Extractor` class.
3. Added `base_production` attribute to the `Good` class.
4. Added `fire_excess` to the `Extractor` class.
5. Added `unemploy_all` method to the `Community` class that sets all its pops' jobs to NONE.
6. Changed how unemployment and employment work. Now unemployed pops will always have Jobs.NONE and pops can only employ pops with Jobs.NONE.
7. Removed the `lru_cached` decorator from the `calc_labor_demand` method.
8. Changed the `promote` property in the `Pop` class to the `can_promote` method.
9. Changed the `job` and `stratum` static methods in the `PopFactory` class to class methods.
10. Changed the static methods in the `ComFactory` class to class methods.
11. Changed all factory methods in the `pop` module such that they will only generate sizes and welfares as low as 0.001
12. Added `__mul__` method to `Stockpile` class.
13. Changed everything in the `goods` module to conform to the minimum floating point of 0.001
14. Refactored the `Impartial` sharing algorithm to make use of the `get_share_of` method in the `Community` class.
15. Fixed the `__filter` method in the `Community` class to return a community with the same objects, not one with identical ones.
16. Created the `reset_to` method in the `Stockpile` class.
17. Created the `Proportional` sharing algorithm.
18. Added the `recipe` attribute to the `Good` dataclass.
19. Turned the `Extractor` class into the `Industry` abstract class and made a new `Extractor` class that inherits from it.
20. Created the `Manufactury` subclass that inherits from `Industry`.