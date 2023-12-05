from __future__ import annotations
from abc import ABC, abstractmethod
from source.exceptions import NegativeAmountError
from source.goods import Stockpile


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
    This strategy shares goods equally regardless of strata. Since not all strata consume the same types or amount of goods,
    this sharing algorithm is inefficient in so that it divides the goods indiscriminately dispite this reality.
    """

    @classmethod
    def share(cls, community: Community, stockpile: Stockpile):

        try:
            divided = stockpile / len(community)
        
        except ZeroDivisionError:
            return

        for pop in community.values():

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

        for community_ in (upper, middle, lower):
            try:
                divided = stockpile / len(community_)
        
            except ZeroDivisionError:
                continue
            
            for pop in community_.values():

                consumption = pop.calc_consumption()
                pop.update_welfare(consumption, divided)

                cls._sub_stock(stockpile, divided, consumption)

class Proportional(SharingAlg):
    """ 
    TODO: make a method that divides the stockpile into three stockpiles each to be distributed to a different strata. It shouldn't
    be divided indiscriminately, but based on constant proportional values giving more to the richer and less to the poorer strata. this
    way ensuring everyone gets at least some good, even if not the same amount.
    """

from source.pop import Community, Strata