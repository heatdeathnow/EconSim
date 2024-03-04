## In order of priority:

- Update `exceptions` module.

- Update all docstrings, comments etc

- `Province` class to mediate production of a province through several industries. Provinces should be able to have different absolute advantages on goods e.g.: only being half as good at producing something so on. Also have it be able to choose with industry gets goods first and so on.

- Move testing of the common behavior of the `Stock` and `Commune` classes to a separate TestCase.

- Learn how to properly import modules such that I can import my classes as type-hints without having to add them to the bottom of the module to avoid circular imports.

- Make it so `Pop` objects decline by different rates than they grow
- Make it so `Pop` objects grow and decline by different rates depending on the stratum
- Make it so `Pop` objects can demote
