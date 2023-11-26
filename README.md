## EconSim
Attemping to create a simulation of an economy similar to that of Victoria II. This will be done entirely in Python.

### Modus Operandi

#### Code hygiene
I will always attempt to fix the code before adding new features. This is the third time I am trying this project. The first time I was still a complete amateur and had never delved into OOP, the second one I had just started learning OOP and things went off the rails pretty quickly. I will refrain myself from adding more features until I review the code and make the changes I think are necessary in order to keep it maintainable and readable. That is not to say that I will always write code like this from the very beginning. I think it is OK to write sloppy code when adding new features, however these new feature additions should be followed by several code reviews and rewrites.

#### OOP
I have learnt OOP recently and I will attempt to use it and its design patterns to the best of my ability. I will not, however, use exclusively OOP just for the sake of using it. If I think a feature would be better implemented in procedural programming then I will use procedural programming. I am not a purist of any form.

### Vision
I want a simulation where populations can have different jobs, strata, cultures and maybe other stuff. These populations should consume goods and change in size over time. They should work on farms and workshops to produces these goods. different goods should be produced in different ways, grains should be planted, iron should be mined, and tools should be crafted from other goods. There should be goods that are replaceable by other goods, e.g.: wheat and corn or beer and wine. There should be internal trading inside a city and external trading from city to city. Cities should be able to put up tarrifs on external goods.

#### List of desired features
1. Population system
    1. Dynamic size through consumption of goods
    2. Jobs based on the population stratum
    3. Employment and unemployment

2. Production system
    1. Primary goods should be extracted from the Earth, such as wheat and iron
    2. Secondary goods should be crafted from primary goods such as tools from iron
    3. Goods should be replaceable like tea and coffee.
    4. Different production methods should become available as a city becomes more advanced.

3. Goods system
    1. Goods should be divided into a goods-group and several exchangeable goods. E.g.: Grain: wheat and corn
    2. Secondary goods should have recipes for crafting.

4. Trading system
    1. Cities should have tariff free internal trading
    2. Cities should be able to raise taxes and do policies.
    3. Cities should be able to trade with other cities.
    4. Cities should be able to raise tariffs on external goods.

5. Biomes
    1. Biomes should dictate how effective a city is in producing certain goods.
    2. Biomes should dictate how liveable a city is.