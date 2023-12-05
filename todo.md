## Improvements:

### Workforce/Extractor/Industry
Change how the `Workforce` class is supposed to be and what it is supposed to achieve. It should contain a `Community` object within itself and specialize on its own things. Maybe merge it with `Extractor`. Maybe have an abstract superclass `Industry` with the intent of having different production methods (e.g.: farming and crafting).
1. Have a `needed_workers` attribute specifying how many workers it needs to produce its good.
2. Have a `produces` attribute specifying the good it produces.
3. Have a `calc_labor_demand` method for getting a `Community` object containing the workers it needs.
4. Have a `calc_efficiency` method that returns considers it 100% if there are more and the same amount of pops in a job that it needs. Change the behaviour so that having more pops than necessary won't lower the efficiency, this should make things easier. Having more pops than necessary would still indirectly make things more inefficient because then the other jobs won't be able to have their desired amount of pops because of the population limit. This should fix ¹.

¹ As of now, there can be a `Workforce` object that is supposed to have 100 `FARMER`s overlooked by 10 `SPECIALIST`s. If this object has 0 farmers and 10 specialists, it has an efficiency of 50%, which is nonsensical.

## Additional features:
### Testing for visualization module.

### Simulation
1. Add functions, classes, and methods to make the simulation code less ugly and more readable.

---
### Goods
1. Give the `Good` class a `throughput`/`base_production` attribute or a way of having different goods have different production _ceteris paribus_.

---
### Population
1. Make it so `Pop` objects decline by different rates than they grow
2. Make it so `Pop` objects grow and decline by different rates depending on the stratum
3. Make it so `Pop` objects can demote
