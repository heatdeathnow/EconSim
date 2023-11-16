## Improvements:

- ### Custom exceptions.

- ### Stockpile
    1. Study the idea of having the link_stockpile method be inherited through a MixIn abstract class.

- ### Workforce
    1. As of now, there can be a `Workforce` object that is supposed to have 100 `FARMER`s overlooked by 10 `SPECIALIST`s. If this object has 0 farmers and 10 specialists, it has an efficiency of 50%, which is nonsensical.

## Additional features:
- ### Population
    1. Make it so `Pop` objects decline by different rates than they grow
    2. Make it so `Pop` objects grow and decline by different rates depending on the stratum
    3. Make it so `Pop` objects can demote
