from visual.gather import DataCase, DataManager
from source.goods import Goods, Stockpile
from source.pop import Jobs, Pop, Strata, pop_factory
from source.prod import extractor_factory, workforce_factory
import warnings

def main():

    """
    ### How should this simulation go about?
    I want to have a wheat_extractor produce some goods and have these goods be redistributed to the population working on the wheat_extractor.
    If they produce more goods than they consume, they should grow over time, if not, they should shrink.

    #### Steps
    1. Production
    2. Consumption
    
    #### Data gathering
    The amount of workers in the workforce and the amount of goods in the stockpile will be recorded twice per tick:
    - Before production
    - Before consumption    
    """

    warnings.simplefilter('ignore', category = FutureWarning)

    stockpile = Stockpile({Goods.WHEAT: 100, Goods.IRON: 100})

    # Wheat farm
    farmer_pops     = pop_factory(45, stockpile, Jobs.FARMER)
    specialist_pops = pop_factory(10, stockpile, Jobs.SPECIALIST)

    workforce = workforce_factory({Jobs.FARMER: 90, Jobs.SPECIALIST: 10}, stockpile, [farmer_pops, specialist_pops])

    wheat_extractor = extractor_factory(workforce, Goods.WHEAT, stockpile)

    # Iron mine
    miner_pops      = pop_factory(45, stockpile, Jobs.MINER)
    specialist_pops_ = pop_factory(10, stockpile, Jobs.SPECIALIST)

    workforce = workforce_factory({Jobs.MINER: 90, Jobs.SPECIALIST: 10}, stockpile, [miner_pops, specialist_pops])

    iron_extractor = extractor_factory(workforce, Goods.IRON, stockpile)

    # Other
    unified_workforce = workforce_factory({Jobs.FARMER: 90, Jobs.MINER: 90, Jobs.SPECIALIST: 20}, stockpile,
                                          [farmer_pops, miner_pops, specialist_pops])
    datacase = DataCase('EconSim-1')
    data_manager = DataManager([datacase])

    idle = pop_factory(0, stockpile, stratum=Strata.MIDDLE)
    for _ in range(150):
        data_manager.data['EconSim-1'] += unified_workforce
        data_manager.data['EconSim-1'] += stockpile

        # Production
        stockpile += wheat_extractor.produce()
        stockpile += iron_extractor.produce()

        data_manager.data['EconSim-1'] += unified_workforce
        data_manager.data['EconSim-1'] += stockpile

        # Consumption
        for pop in unified_workforce.pops.values():
            promotion = pop.consume()

            if promotion: idle += promotion
        
        half = idle.size / 2
        first_half, second_half = idle, idle
        
        first_half = wheat_extractor.employ(first_half)
        second_half = iron_extractor.employ(second_half)

        idle = idle = pop_factory(first_half.size + second_half.size, stockpile, stratum=Strata.MIDDLE)

    data_manager.save_csv('EconSim-1', overwrite = True)
    data_manager.plot_graph('EconSim-1')

# def main(): import tests

if __name__ == '__main__':
    main()
    