import copy
from random import shuffle
import warnings
from source.algs import proportional, retrospective
from source.goods import Techs, Products, create_stock
from source.pop import CommuneFactory, Jobs
from source.prod import Industry, IndustryFactory
from visual.gather import DataManager
from decimal import ROUND_HALF_DOWN, Context, DivisionByZero, InvalidOperation, setcontext

def main():
    warnings.simplefilter(action='ignore', category=FutureWarning)

    data_name = 'EconSim'

    WHEAT = Products.WHEAT
    IRON = Products.IRON
    FLOUR = Products.FLOUR

    FARMER = Jobs.FARMER
    MINER = Jobs.MINER
    CRAFTSMAN = Jobs.CRAFTSMAN
    SPECIALIST = Jobs.SPECIALIST

    CRAFTING = Techs.CRAFTING
    MILLING = Techs.MILLING

    farm = IndustryFactory.create_industry(WHEAT, {FARMER: 990, SPECIALIST: 10}, {FARMER: 200, SPECIALIST: 5})
    mine = IndustryFactory.create_industry(IRON, {MINER: 990, SPECIALIST: 10}, {MINER: 200, SPECIALIST: 5})
    flour_craft = IndustryFactory.create_industry(FLOUR, {CRAFTSMAN: 990, SPECIALIST: 10}, {CRAFTSMAN: 200, SPECIALIST: 5}, CRAFTING)
    flour_mill = IndustryFactory.create_industry(FLOUR, {CRAFTSMAN: 990, SPECIALIST: 10}, {CRAFTSMAN: 200, SPECIALIST: 5}, MILLING)

    common_stock = create_stock({WHEAT: 500, IRON: 500})
    jobless_pops = CommuneFactory.create_by_job()
    
    communes = [farm.workforce, mine.workforce, flour_craft.workforce, flour_mill.workforce, jobless_pops]
    industries: list[Industry] = [farm, mine, flour_craft, flour_mill]
    manufacturies = [flour_craft, flour_mill]

    data_manager = DataManager(data_name, farm, mine, flour_craft, flour_mill, jobless_pops)

    for _ in range(200):

        # ---------------------- PRODUCTION ------------------------
        data_manager.record_goods_satisfaction(common_stock)

        before = copy.deepcopy(common_stock)

        for industry in industries:
            common_stock += industry.produce()

        data_manager.record_goods_produced(before, common_stock)
        data_manager.record_stockpile(common_stock)

        # --------------------- CONSUMPTION ------------------------
        original_stock = copy.deepcopy(common_stock)
        data_manager.record_goods_demanded()

        shuffle(manufacturies)
        for manufactury in manufacturies:
            manufactury.restock(common_stock)

        shuffle(industries)
        for industry in industries:
            industry.workforce.update_welfares(common_stock, proportional)

        jobless_pops.update_welfares(common_stock, proportional)
        
        data_manager.record_pop_welfare()
        data_manager.record_goods_consumed(original_stock, common_stock)
        
        # ----------------------- RESIZING -------------------------
        for commune in communes:
            commune.resize_all()
        
        # ----------------------- PROMOTION ------------------------
        # The fact that promotion goes after resizing does affect the behavior of the simulation, for the promotions will be larger this way.
        for commune in communes:
            if commune is jobless_pops: continue
            jobless_pops += commune.promote_all()

        # ----------------------- EMPLOYMENT -----------------------
        shuffle(industries)  # TODO implement an algorithm for choosing what Extractor gets the goods first, or that divides it between them.
        for industry in industries:
            for pop in jobless_pops.values():
                if industry.can_employ(pop):
                    industry.employ(pop)
        
        # ---------------------- REBALANCING -----------------------
        for industry in industries:
            if industry.workforce.size > industry.capacity:
                jobless_pops += industry.fire_excess()

            if industry.is_unbalanced():
                jobless_pops += industry.balance(retrospective)

        data_manager.record_pop_size()
    
    data_manager.save_csv(True)
    data_manager.plot_all()

if __name__ == '__main__':

    context = Context(rounding=ROUND_HALF_DOWN, traps=[DivisionByZero, InvalidOperation])

    if False:
        import tests
        exit()

    setcontext(context)
    main()
