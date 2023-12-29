from random import shuffle
import warnings
from source.goods import Goods, Stockpile
from source.pop import Community, Jobs
from source.prod import ExtFactory
from source.utils import RichFirst
from visual.gather import DataCase, DataManager


def main():
    warnings.simplefilter(action='ignore', category=FutureWarning)

    data_name = 'EconSim'
    data = DataCase(data_name)

    wheat_farm = ExtFactory.default(Goods.WHEAT, {Jobs.FARMER: 900, Jobs.SPECIALIST: 100}, {Jobs.FARMER: 450, Jobs.SPECIALIST: 50})
    iron_mine = ExtFactory.default(Goods.IRON, {Jobs.MINER: 900, Jobs.SPECIALIST: 100}, {Jobs.MINER: 450, Jobs.SPECIALIST: 50})
    stockpile = Stockpile({Goods.WHEAT: 2500, Goods.IRON: 100})
    unemployed = Community()

    random = [wheat_farm, iron_mine]

    for _ in range(150):

        # ---------------------- PRODUCTION ------------------------
        goods_produced = wheat_farm.produce()
        goods_produced += iron_mine.produce()
        data.record_goods_produced(goods_produced)
        stockpile += goods_produced
        data.record_stockpile(stockpile)

        # --------------------- CONSUMPTION ------------------------ 
        shuffle(random)  # TODO implement an algorithm for choosing what Extractor gets the goods first, or that divides it between them.
        for extractor in random:
            extractor.workforce.update_welfares(stockpile, RichFirst)  # This modifies the stockpile in place.
        
        data.record_pop_welfare(wheat_farm.workforce + iron_mine.workforce)
        data.record_goods_demanded((wheat_farm.workforce + iron_mine.workforce).calc_goods_demand())
        
        # ----------------------- RESIZING -------------------------
        wheat_farm.workforce.resize_all()
        iron_mine.workforce.resize_all()

        # ----------------------- PROMOTION ------------------------
        # The fact that promotion goes after resizing does affect the behavior of the simulation, for the promotions will be larger this way.
        unemployed += wheat_farm.workforce.promote_all()
        unemployed += iron_mine.workforce.promote_all()

        # ----------------------- EMPLOYMENT -----------------------
        shuffle(random)  # TODO implement an algorithm for choosing what Extractor gets the goods first, or that divides it between them.
        for extractor in random:
            for pop in unemployed.values():
                if extractor.can_employ(pop):
                    extractor.employ(pop)  # This modifies the pop in place.

        data.record_pop_size(wheat_farm.workforce + iron_mine.workforce)
    
    manager = DataManager(data)
    manager.save_csv(data_name, True)
    manager.plot_all(data_name)

def test():
    import tests

if __name__ == '__main__':
    main()
