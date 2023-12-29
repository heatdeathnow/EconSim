## In order of priority:

- Investigate why the welfare of the SPECIALISTs in the simulation won't drop below 0.2 even though they are dying off.

- Give the `Good` class a `throughput`/`base_production` attribute or a way of having different goods have different production _ceteris paribus_.

- Write the `Recipe` class to mediate crafting of goods.

- Add the `Manufactury` class, it together with `Extractor` should be subclasses of `Industry`. `Manufactury` objects will behave similar to `Extractor` objects, but will intake goods in order to produce other goods. E.g.: intake wood, produce lumber.

- Learn how to properly import modules such that I can import my classes as type-hints without having to add them to the bottom of the module to avoid circular imports.

- Study the possibility and consider changing how the testing subpackage works, removing redundant and repetitive code. Maybe move it out to abstract superclasses and have the testing classes inherit from it to use its functionality instead of rewriting it for everything?

- Make it so `Pop` objects decline by different rates than they grow
- Make it so `Pop` objects grow and decline by different rates depending on the stratum
- Make it so `Pop` objects can demote
