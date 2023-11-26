## Improvements:

### Population
High level methods for manipulating `Workforce` objects or manipulating several `Pop` objects all at once:
1. Calculate the demand of goods for everyone.
2. Calculate the demand of labor for the workforce.  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! *
3. A method for updating the `welfare` for every pop in a workforce via a passed stockpile.
4. A method for updating the `size` for every pop in a workforce via their welfare.
5. A method for promoting all the pops in a workforce that can be promoted.

* Study the possibility of having another class to interface the `Extractor` and the `Workforce` so that the `Workforce` doesn't need a `needed_jobs` attribute or something similar.

### Exceptions
1. Add `NegativeAmountError`

---
### Simulation
2. Go over the simulation code and add special methods to the `Pop`, `Workforce` etc classes in order to make manipulating them more easily based on what I need to do in the simulation.

---
### Workforce / Extractor
1. As of now, there can be a `Workforce` object that is supposed to have 100 `FARMER`s overlooked by 10 `SPECIALIST`s. If this object has 0 farmers and 10 specialists, it has an efficiency of 50%, which is nonsensical.
2. Move the calculation of the `labor_demand` and the `needed_jobs` attribute either to the `Extractor` class, or to the possible new interface class that will intermediate this.

---
### Stockpile
1. Study the idea of having the link_stockpile method be inherited through a MixIn abstract class.

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
