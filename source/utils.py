from __future__ import annotations
from abc import ABC, abstractmethod
import copy
import math
from source.exceptions import NegativeAmountError
from source.goods import Stockpile

# ===================== Sharing algorithms =====================
class SharingAlg(ABC):

    @classmethod
    @abstractmethod
    def share(cls, community: Community, stockpile: Stockpile):
        """
        This abstract method is the method through which the distribution will be done. The strategy subclasses will implement
        different ways of ditributing goods between pops in a community. Regarless of implementation, it will always update 
        the welfare of all pops of the community passed and will always subtract the used goods from the stockpile.
        """
    
    @staticmethod
    def _sub_stock(real_stockpile: Stockpile, calc_stockpile: Stockpile, consumption: Stockpile):
        """
        This private method subtracts from a `stockpile` object representing an actual stockpile all it can subtract from 
        another consumption `Stockpile` object. All the negative amount check are already done in the stockpile class 
        through the `NegativeAmountError` exception.
        """

        for good, wanted_amount in consumption.items():
            removed = min(wanted_amount, calc_stockpile[good])
            real_stockpile[good] -= removed

class FirstInFirstServed(SharingAlg):
    """
    This sharing method iterates over the pops in the community indiscriminately and 
    distributes the goods with priority to whomever shows up first.
    """

    @classmethod
    def share(cls, community: Community, stockpile: Stockpile):

        for pop in community.values():
            consumption = pop.calc_consumption()
            pop.update_welfare(consumption, stockpile)
            cls._sub_stock(stockpile, stockpile, consumption)

class Impartial(SharingAlg):
    """
    This strategy shares goods equally based on size and regardless of strata. Since not all strata consume the same types or 
    amount of goods, this sharing algorithm is inefficient in so that it divides the goods indiscriminately dispite this reality.
    """

    @classmethod
    def share(cls, community: Community, stockpile: Stockpile):

        original = copy.deepcopy(stockpile)
        for job, pop in community.items():
            
            share = community.get_share_of(job)
            divided = original * share

            consumption = pop.calc_consumption()
            pop.update_welfare(consumption, divided)
            cls._sub_stock(stockpile, divided, consumption)

class RichFirst(SharingAlg):
    """
    This sharing algorithm iterates through the pops in order of stratum. Richer strata are allowed to consume 
    from the stockpile before the poorer ones. It divides the stockpile in each iteration depending on the amount 
    of pops of that specific stratum. This algorithm is inefficient because it does not guarantee all pops will 
    get goods, not even a skewed amount.
    """

    @classmethod
    def share(cls, community: Community, stockpile: Stockpile):

        upper = community[Strata.UPPER]
        middle = community[Strata.MIDDLE]
        lower = community[Strata.LOWER]

        for current_community in (upper, middle, lower):
            original = copy.deepcopy(stockpile)

            for job, pop in current_community.items():
                share = current_community.get_share_of(job)
                divided = original * share

                consumption = pop.calc_consumption()
                pop.update_welfare(consumption, divided)
                cls._sub_stock(stockpile, divided, consumption)

class Proportional(SharingAlg):
    """ 
    TODO: make a method that divides the stockpile into three stockpiles each to be distributed to a different strata. It shouldn't
    be divided indiscriminately, but based on constant proportional values giving more to the richer and less to the poorer strata. this
    way ensuring everyone gets at least some good, even if not the same amount.
    """

    UPPER_WEIGHT  = .50
    MIDDLE_WEIGHT = .35
    LOWER_WEIGHT  = .15

    assert math.isclose(UPPER_WEIGHT + MIDDLE_WEIGHT + LOWER_WEIGHT, 1)

    @classmethod
    def share(cls, community: Community, stockpile: Stockpile):
        stockpiles = {Strata.UPPER: Stockpile({good: amount * cls.UPPER_WEIGHT for good, amount in stockpile.items()}),
                      Strata.MIDDLE: Stockpile({good: amount * cls.MIDDLE_WEIGHT for good, amount in stockpile.items()}),
                      Strata.LOWER: Stockpile({good: amount * cls.LOWER_WEIGHT for good, amount in stockpile.items()})}
        
        left_overs = Stockpile()
        for stratum in (Strata.UPPER, Strata.MIDDLE, Strata.LOWER):
            current_community = community[stratum]
            stockpiles[stratum] += left_overs

            if current_community.size == 0:
                left_overs = stockpiles[stratum]
                continue

            original = copy.deepcopy(stockpiles[stratum])
            for job, pop in current_community.items():
                share = current_community.get_share_of(job)
                divided = original * share

                consumption = pop.calc_consumption()
                pop.update_welfare(consumption, divided)
                cls._sub_stock(stockpiles[stratum], divided, consumption)
            
            left_overs = stockpiles[stratum]
        
        stockpile.reset_to(left_overs)

# ===================== Unemployment algorithms =====================
class BalanceAlg(ABC):
    
    @classmethod
    @abstractmethod
    def balance(cls, ext: Industry) -> Community:
        """
        This absctract method's implementations will be responsible for unemploying pops from an extractor based on the
        desired proportion of the working population's jobs. The resposibility of unemploying pops from overcapacity should be
        handled by the `Extractor` class itself.
        """
    
    @staticmethod
    def _get_removed(desired_share: int | float, total_size: int | float, pop: Pop) -> Pop:
        """ Refer to the formulas index. """

        return PopFactory.job(pop.job, - ((desired_share * total_size - pop.size) / (1 + desired_share)), pop.welfare)

class Retrospective(BalanceAlg):
    
    @classmethod
    def balance(cls, ext: Extractor) -> Community:
        """ 
        This solution changes the workforce inplace therefore it allows the next calculations to be done with the new size of the 
        workforce in mind. This solution is flawed because the first jobs to unemploy do not take into account the change in total
        size that the unemployment by the next jobs will cause.
        
        TODO: generalize this so that it works when a specific job is unavailable. In the current form, it will slowly lose popupation
        as it unemploys pops trying to make those 0 pops of a job it doesn't have reach the desired share.
        """

        total_unemployed = Community()

        for job, pop in ext.workforce.items():

            if ext.workforce.get_share_of(job) > ext.efficient_shares[job]:  # type: ignore
                unemployed = cls._get_removed(ext.efficient_shares[job], ext.workforce.size, pop)  # type: ignore 
                ext.workforce -= unemployed
                total_unemployed += unemployed

        total_unemployed.unemploy_all()
        return total_unemployed

class Iterative(BalanceAlg):

    ITERATIONS = 3

    @classmethod
    def balance(cls, ext: Extractor):
        total_unemployed = Community()

        for _ in range(cls.ITERATIONS):

            for job, pop in ext.workforce.items():

                if ext.workforce.get_share_of(job) > ext.efficient_shares[job]:  # type: ignore
                    unemployed = cls._get_removed(ext.efficient_shares[job], ext.workforce.size, pop)  # type: ignore 
                    ext.workforce -= unemployed
                    total_unemployed += unemployed
                    
        total_unemployed.unemploy_all()        
        return total_unemployed

from source.pop import Community, Jobs, Strata, Pop, PopFactory, ComFactory
from source.prod import Extractor, Industry
