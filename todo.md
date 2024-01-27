## In order of priority:

- Find a better way to represent goods than an Enum.

- Add the `Manufactury` class, it together with `Extractor` should be subclasses of `Industry`. `Manufactury` objects will behave similar to `Extractor` objects, but will intake goods in order to produce other goods. E.g.: intake wood, produce lumber.

- `Province` class to mediate production of a province through several industries. Provinces should be able to have different absolute advantages on goods e.g.: only being half as good at producing something so on.

- Learn how to properly import modules such that I can import my classes as type-hints without having to add them to the bottom of the module to avoid circular imports.

- Study the possibility and consider changing how the testing subpackage works, removing redundant and repetitive code. Maybe move it out to abstract superclasses and have the testing classes inherit from it to use its functionality instead of rewriting it for everything?

- Make it so `Pop` objects decline by different rates than they grow
- Make it so `Pop` objects grow and decline by different rates depending on the stratum
- Make it so `Pop` objects can demote
