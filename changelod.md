1. The previous `Pop` "dataclass" has been broken up into a proper `Pop` dataclass and a `Community` class.
2. The aforementioned `Community` class split from `Pop` has been merged with the previous `Workforce` class from the `prod` module.
3. Added `NONE` to the `Jobs` enum. This will from now on substitute the built-in `None`.
4. Changed the `consumption` property to the `calc_consumption` method.
5. The previous `welfare` property in the `Pop` class has been broken up into the `welfare` attribute and the `update_welfare` method.
6. The `consume` method in the `Pop` class has been scrapped.
7. A new `resize` method in the `Pop` class has been created for modifying its size based on its previous size and its current welfare.
8. A new `promote` method in the `Pop` class has been create for dealing with promotion on all strata.
9. Replaced the `pop_factory` function with the PopFactory class which is responsible for implementing several factory methods.
10. Added the `job` method to the `PopFactory` class, which is responsible for instantiating a `Pop` via a desired job.
11. Added the `stratum` method to the `PopFactory` class which instantiates a `Pop` with `NONE` as a job via the desired stratum.
12. Renamed the `fix` method in the `Community` and `Stockpile` classes to `__fix` to make it explicit that it is a private method.
13. `jobs` property in the `Strata` enum has replaced the `JOBS` dictionary and the `needs` property has replaced the `NEEDS` dictionary.
14. The `promotes` property in the `Strata` enum has replace the `promotes` post-initialized attribute previously present in the `Pop` class.
15. Added the `stratum` property to the `Jobs` dictionary that specifies which stratum can hold each specific job.
16. Added the `promotes` method in the `Pop` class for determining if an object can promote.
17. Unittested the new `PopFactory` class and the modified `Pop` class.
18. Made the `Community` class more flexible and easy to work with. Consult docs.
19. Created the `ComFactory` class for creating `Community` objects.
20. Tested the `Pop`, `PopFactory`, `Community`, and `ComFactory` classes.