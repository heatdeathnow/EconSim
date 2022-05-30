from random import shuffle
from math import floor
import variables


def assess():
    variables.money_supply = 0
    variables.population = 0
    variables.total_demand = [0] * len(variables.goods)
    variables.total_supply = [0] * len(variables.goods)
    for commune in variables.communes:
        variables.money_supply += commune.money
        variables.population += commune.size

        id = 0
        for demand in commune.total_demand:
            if demand >= 0:
                variables.total_demand[id] += demand

            else:
                variables.total_supply[id] -= demand

            id += 1


def exchange():
    order = variables.communes[:]
    shuffle(order)

    for commune in order:
        for need in commune.needs:

            bought = min(commune.survival_demand[need[0]], floor(commune.money / variables.prices[need[0]]),
                         variables.total_supply[need[0]])
            spent = bought * variables.prices[need[0]]

            commune.goods[need[0]] += bought
            commune.money -= spent

            variables.communes[need[0]].goods[need[0]] -= bought
            variables.communes[need[0]].money += spent

            variables.total_supply[need[0]] -= bought

        try:
            for need in variables.goods[commune.produces].recipe:

                bought = min(commune.production_demand[need],
                             floor(commune.money / variables.prices[need]), variables.total_supply[need])
                spent = bought * variables.prices[need]

                commune.goods[need] += bought
                commune.money -= spent

                variables.communes[need].goods[need] -= bought
                variables.communes[need].money += spent

                variables.total_supply -= bought

        except TypeError:
            pass

    # As trocas cessaram, análise da movimentação dos estoques:
    for commune in variables.communes:

        lower_threshold = commune.size * variables.goods[commune.produces].production_rate
        upper_threshold = commune.size * variables.goods[commune.produces].production_rate * 2

        # Se os estoques estão em uma situação crítica:
        if commune.goods[commune.produces] <= lower_threshold:
            variables.prices[commune.produces] *= 1.5
            commune.compensation += 0.25

        # Se há excesso de estoques:
        elif commune.goods[commune.produces] > upper_threshold:
            variables.prices[commune.produces] *= 0.5
            commune.compensation -= 0.025

        commune.compensation = round(commune.compensation, 3)
        variables.prices[commune.produces] = round(variables.prices[commune.produces])

        if commune.compensation > 1:
            commune.compensation = 1
        elif commune.compensation < 0:
            commune.compensation = 0

        if variables.prices[commune.produces] <= 0:
            variables.prices[commune.produces] = 1
        elif variables.prices[commune.produces] >= variables.money_supply:
            variables.prices[commune.produces] = variables.money_supply


def record():
    variables.price_memory = variables.prices[:]
    variables.demand_memory = variables.total_demand[:]
    variables.supply_memory = variables.total_supply[:]
