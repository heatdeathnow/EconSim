1. Scrapped the old goods system.
2. Created the `Production` class that from now on will store the `base_yield` attribute, and no or several recipes for a good.
3. Created the `Products` Enum that works as a index for types of goods and their information through the `production_methods` property.
4. Created the `Good` dataclass that will function as an actual representation of physical goods circulating and being consumed.
5. Created the `create_good` function for boilerplate checks over the instantiation of goods.
6. Changed the `Stockpile` class to work with instances of `Good` instead of ints.
8. Created the `ProdTech` Enum.
9. Refactored all unittesting to be done more concisely.
10. Created the `Dyct` abstract class whom `Stockpile` and `Community` now inherit their shared behavior from.
11. Removed the `__scrutinize` method from both `Stockpile` and `Community`.
12. Renamed:
    * `Jobs.NONE` -> `Jobs.UNEMPLOYED`
    * `Community` -> `Commune`
    * `ComFactory` -> `CommuneFactory`
    * `stock_factory` -> `create_stock`
    * `Stockpile` -> `Stock`
    * `Good.__scrutinize` -> `Good._scrutinize`
    * `Pop.__scrutinize` -> `Pop._scrutinize`
    * `Community` -> `Commune`
13. Made most callables positional-only.
14. Removed manual implementation of the rich comparison operators for the dataclasses and instead began using `order=True`.
15. Create the `Group` abstract class to pull out common behaviour of the `Pop` and `Good` classes.
16. Changed all numerical things to the `Decimal` type.
17. Rewrote all factory classes and factory functions.
18. Rewrote all algorithms to be functions and not classes.
19. Refactored all graphs
20. Added demand satisfaction graph.