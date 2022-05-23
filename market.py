import math
from random import shuffle
from math import floor
import variables


def assess():
    variables.money_supply = 0
    variables.population = 0
    variables.total_demand = [0] * len(variables.goods)
    variables.total_supply = [0] * len(variables.goods)
    variables.prices = [0] * len(variables.goods)
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

    id = 0
    while id < len(variables.prices):
        try:
            # Preço = (Demanda / Oferta) * (Q.Monetária / Q.População) / (V. Monetária)
            variables.prices[id] = math.floor(
                variables.total_demand[id] * variables.money_supply
                / variables.total_supply[id] / variables.population / variables.money_velocity
            )

        except ZeroDivisionError:
            variables.prices[id] = float('inf')
        id += 1


def exchange():
    order = variables.communes[:]
    shuffle(order)

    for commune in order:
        for need in commune.needs:

            if variables.prices[need[0]] == float('inf'):
                spent = 0
                bought = 0

            else:
                try:
                    bought = min(commune.survival_demand[need[0]], floor(commune.money / variables.prices[need[0]]),
                                 variables.total_supply[need[0]])
                except ZeroDivisionError:
                    bought = min(commune.survival_demand[need[0]], variables.total_supply[need[0]])

                spent = bought * variables.prices[need[0]]

            commune.goods[need[0]] += bought
            commune.money -= spent

            variables.communes[need[0]].goods[need[0]] -= bought
            variables.communes[need[0]].money += spent

            variables.total_supply[need[0]] -= bought

        try:
            for need in variables.goods[commune.produces][1]:

                if variables.prices[need[0]] == float('inf'):
                    spent = 0
                    bought = 0

                else:
                    try:
                        bought = min(commune.production_demand[need[0]],
                                     floor(commune.money / variables.prices[need[0]]), variables.total_supply[need[0]])
                    except ZeroDivisionError:
                        bought = min(commune.production_demand[need[0]], variables.total_supply[need[0]])

                    spent = bought * variables.prices[need[0]]

                commune.goods[need[0]] += bought
                commune.money -= spent

                variables.communes[need[0]].goods[need[0]] -= bought
                variables.communes[need[0]].money += spent

                variables.total_supply -= bought

        except TypeError:
            pass

    # As trocas cessaram, analise da movimentação dos estoques:
    for commune in variables.communes:
        # Se a comuna já tem mais ou o que produziria em um turno no inventário, ela vai diminuir a produção
        if commune.goods[commune.produces] > variables.production_rate * commune.size and commune.compensation > 0:
            commune.compensation -= 0.05

        elif commune.goods[commune.produces] <= variables.production_rate * commune.size and commune.compensation < 1:
            commune.compensation += 0.1

        commune.compensation = round(commune.compensation, 2)
