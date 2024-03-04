from __future__ import annotations
from source.pop import PopFactory, CommuneFactory, Strata
from decimal import Decimal, getcontext
from typing import TYPE_CHECKING, Callable
from source.goods import create_stock
from source.goods import Stock
import copy
D = getcontext().create_decimal

if TYPE_CHECKING:
    from source.pop import Commune, Pop
    from source.prod import Industry

# ===================== Sharing algorithms =====================

type sharing_alg = Callable[[Commune, Stock], None]

def _sub_stock(real_stockpile: Stock, calc_stockpile: Stock, consumption: Stock, /):
    """
    This function subtracts from a `stockpile` object representing an actual stockpile all it can subtract from 
    another consumption `Stock` object. All the negative amount check are already done in the stockpile class 
    through the `NegativeAmountError` exception.
    """

    for product, wanted_good in consumption.items():
        removed = min(wanted_good, calc_stockpile[product])
        real_stockpile[product] -= removed

def first_in_first_served(community: Commune, stockpile: Stock, /):
    """ 
    The first pop to be retrieved in the loop gets to pick from the entire stockpile, and the next gets to pick
    the its remaints and so on.
    """

    for pop in community.values():
        consumption = pop.calc_consumption()
        pop.update_welfare(consumption, stockpile)
        _sub_stock(stockpile, stockpile, consumption)

def impartial(community: Commune, stockpile: Stock, /):
    """
    Divides the stock into amounts that reflect each pop's size and that's their cut of the stockpile. If a pop does not consume
    all its share, it is _not_ reintroduced into the stock.
    """

    original = copy.deepcopy(stockpile)

    for job, pop in community.items():
        share = community.get_share_of(job)
        divided = original * share

        consumption = pop.calc_consumption()
        pop.update_welfare(consumption, divided)  #type: ignore
        _sub_stock(stockpile, divided, consumption)  #type: ignore

def rich_first(community: Commune, stockpile: Stock, /):
    """
    Divides the pops into their strata and iterate by order of stratum. The stock is cut once every iteration depending on
    the proportions of the pops in that stratum.
    """
    
    upper = community[Strata.UPPER]
    middle = community[Strata.MIDDLE]
    lower = community[Strata.LOWER]

    for current_community in (upper, middle, lower):
        original = copy.deepcopy(stockpile)

        for job, pop in current_community.items():
            share = current_community.get_share_of(job)
            divided = original * share

            consumption = pop.calc_consumption()
            pop.update_welfare(consumption, divided)  # type: ignore
            _sub_stock(stockpile, divided, consumption)  # type: ignore

def proportional(community: Commune, stockpile: Stock, /):
    """
    Iterates with stratum priority, but each stratum only gets a fixed amount of the stock. If the stratum does not consume
    the entire stock, it is then added to the next stratum's stock.
    """
    
    UPPER_WEIGHT  = D('.50')
    MIDDLE_WEIGHT = D('.35')
    LOWER_WEIGHT  = D('.15')

    stockpiles = {Strata.UPPER: Stock({good: amount * UPPER_WEIGHT for good, amount in stockpile.items()}),
                  Strata.MIDDLE: Stock({good: amount * MIDDLE_WEIGHT for good, amount in stockpile.items()}),
                  Strata.LOWER: Stock({good: amount * LOWER_WEIGHT for good, amount in stockpile.items()})}
    
    left_overs = create_stock()
    for stratum in (Strata.UPPER, Strata.MIDDLE, Strata.LOWER):
        current_community = community[stratum]
        stockpiles[stratum] += left_overs

        if current_community.size == D(0):
            left_overs = stockpiles[stratum]
            continue

        original = copy.deepcopy(stockpiles[stratum])
        for job, pop in current_community.items():
            share = current_community.get_share_of(job)
            divided = original * share
            consumption = pop.calc_consumption()
            pop.update_welfare(consumption, divided)  # type: ignore
            _sub_stock(stockpiles[stratum], divided, consumption)  # type: ignore
        
        left_overs = stockpiles[stratum]
    
    stockpile.reset_to(left_overs)

# ===================== Unemployment algorithms =====================
    
type balance_alg = Callable[[Industry], Commune]

def _get_removed(desired_share: Decimal, total_size: Decimal, pop: Pop, /) -> Pop:
    """ Refer to the formulas index. """

    return PopFactory.job_makepop(pop.job, - ((desired_share * total_size - pop.size) / (1 + desired_share)), pop.welfare)

def retrospective(ext: Industry, /) -> Commune:
    """ 
    This solution changes the workforce inplace therefore it allows the next calculations to be done with the new size of the 
    workforce in mind. This solution is flawed because the first jobs to unemploy do not take into account the change in total
    size that the unemployment by the next jobs will cause.
    
    TODO: generalize this so that it works when a specific job is unavailable. In the current form, it will slowly lose popupation
    as it unemploys pops trying to make those 0 pops of a job it doesn't have reach the desired share.
    """

    total_unemployed = CommuneFactory.create_by_job()

    for job, pop in ext.workforce.items():
        if ext.workforce.get_share_of(job) > ext.efficient_shares[job]:  # type: ignore
            unemployed = _get_removed(ext.efficient_shares[job], ext.workforce.size, pop)  # type: ignore 
            ext.workforce -= unemployed
            total_unemployed += unemployed

    total_unemployed.unemploy_all()
    return total_unemployed

def iterative(ext: Industry, /):
    """
    The same as retrospective, but done x times in a row in order to make it more precise.
    """
    
    ITERATIONS = 3

    total_unemployed = CommuneFactory.create_by_job()

    for _ in range(ITERATIONS):
        total_unemployed += retrospective(ext)
                
    return total_unemployed
