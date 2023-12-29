1. Added the cached_property `efficient_proportion` to the `Extractor` class.
2. Reordered the parameters in `Extractor`'s `__init__` method.
3. Added `size` property to the `Community` class.
4. Removed `calc_total_workers` method from the `Extractor` class.
5. Changed the `calc_efficiency` method of the `Extractor` class back to a proportion-based approach.
6. Removed the `calc_goods_demand` method from the `Extractor` class.
7. Refactored the `calc_labor_demand` method in the `Extractor` class to return a `Community` object.
8. Removed the `__fix_dict` private method from the `Extractor` class.
9. Added numerical comparison special methods to the `Pop` class.
10. Added `float` casts to the NumPy average function calls in the `Pop` class.
11. Changed the `employ` method to no longer employ pops whose job is Jobs.NONE to the first job on the dictionary. Now it gives it to the one with the most demand.
12. Changed the `can_employ` method to take into account if pops whose job is Jobs.NONE can be employed based if there are jobs of their stratum in the labor demand.
13. Removed the `__employable_strata` private property.
14. Testing for the comparison operators in the `Pop` class.
15. Added `ZeroDivisionError` boilerplate to the other operator overwrites in the `Pop` class in order to fix a crash.
16. Testing for the changes in the `Extractor` class.
17. Changed the `record_production` usage to actually record the production instead of the stockpile. Added the `record_stockpile` method in its old place.