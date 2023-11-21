## Improvements:

- ### Testing for visualization module.

- ### Population
    1. Study the possibility of having the `Pop` class be instead a container of populations of different jobs instead of just one population with just one job. This could make the code easier, but would require a lot of rewriting.

- ### Stockpile
    1. Study the idea of having the link_stockpile method be inherited through a MixIn abstract class.

- ### Workforce
    1. As of now, there can be a `Workforce` object that is supposed to have 100 `FARMER`s overlooked by 10 `SPECIALIST`s. If this object has 0 farmers and 10 specialists, it has an efficiency of 50%, which is nonsensical.

- ### Simulation
    1. Add functions, classes, and methods to make the simulation code less ugly and more readable.
    2. Go over the simulation code and add special methods to the `Pop`, `Workforce` etc classes in order to make manipulating them more easily based on what I need to do in the simulation.

## Additional features:
- ### Population
    1. Make it so `Pop` objects decline by different rates than they grow
    2. Make it so `Pop` objects grow and decline by different rates depending on the stratum
    3. Make it so `Pop` objects can demote
