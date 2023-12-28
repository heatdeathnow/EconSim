1. Changed the `workforce` attribute of the `Extractor` class to take in `Community` objects.
2. Added the `needed_workers` attribute to the `Extractor` class which is a `dict[Jobs, int | float]`.
3. Added the `capacity` cached property to the `Extractor` class.
4. Changed the efficiency property to the `calc_efficiency` method.
5. Changed how the `calc_efficiency` method works, now sizes over that which is needed won't be considered.
6. Moved `labor_demand` from the old Workforce class to the `Extractor` class and renamed it to `calc_labor_demand`
7. Refactored `calc_labor_demand` making it more readable.
8. Created the `__fix_dict` private static method in the `Extractor` class for removing zeroes from dictionaries.
9. Moved the `goods_demand` method to the `Extractor` class and renamed it `calc_goods_demand`.
10. The `employ` method now expected that the passed pop is either of a demanded job or `Jobs.NONE`. It no longer returns the remains of the employed pop, it just modifies it in place.
11. Created the `can_employ` method to check if the `Extractor` object can employ a `Pop` object.
12. Created the `Extfactory` class with validation methods and two factory methods: `default` and `full`.
13. Added the `lru_cache` decorator to the `calc_labor_demand` method, because it seemed expensive and often used.
14. Added testing to the refactored `prod` module.
15. Refactored the simulation itself.
16. Refactored the visualization module.