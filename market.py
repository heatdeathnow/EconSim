from random import shuffle
import variables


def assess():
    variables.money_supply = 0
    variables.total_demand = [0] * len(variables.goods)
    variables.total_supply = [0] * len(variables.goods)
    variables.prices = [0] * len(variables.goods)
    for commune in variables.communes:
        variables.money_supply += commune.money

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
            variables.prices[id]\
                = round((variables.money_supply * variables.total_demand[id]) / (variables.total_supply[id] ** 2))

        except ZeroDivisionError:
            variables.prices[id] = float('inf')
        id += 1


def exchange():
    order = variables.communes[:]
    shuffle(order)

    for commune in order:
        for need in commune.needs:

            if variables.prices[need[0]] == 0:
                spent = 0
                bought = commune.survival_demand[need[0]]

            elif variables.prices[need[0]] == float('inf'):
                spent = 0
                bought = 0

            # Demanda <= Pode comprar & Demanda <= Oferta - situação 1, compra tudo que precisa
            elif (commune.survival_demand[need[0]] <= commune.money / variables.prices[need[0]]
                    and commune.survival_demand[need[0]] <= variables.total_supply[need[0]]):
                spent = variables.prices[need[0]] * commune.survival_demand[need[0]]
                bought = commune.survival_demand[need[0]]

            # Pode comprar <= Demanda & Pode comprar <= Oferta - situação 2, compra tudo o que consegue
            elif (commune.money / variables.prices[need[0]] <= commune.survival_demand[need[0]]
                  and commune.money / variables.prices[need[0]] <= variables.total_supply[need[0]]):
                spent = commune.money
                bought = round(commune.money / variables.prices[need[0]])

            # O min(demanda, pode comprar) é maior que a oferta - situação 3, compra tudo que há no mercado
            else:
                spent = variables.prices[need[0]] * variables.total_supply[need[0]]
                bought = variables.total_supply[need[0]]

            commune.goods[need[0]] += bought
            commune.money -= spent

            variables.communes[need[0]].goods[need[0]] -= bought
            variables.communes[need[0]].money += spent

            variables.total_supply[need[0]] -= bought

        try:
            for need in variables.goods[commune.produces][2]:

                if variables.prices[need[0]] == 0:
                    spent = 0
                    bought = commune.production_demand[need[0]]

                elif variables.prices[need[0]] == float('inf'):
                    spent = 0
                    bought = 0

                # Demanda <= Pode comprar & Demanda <= Oferta - situação 1, compra tudo que precisa
                elif (commune.production_demand[need[0]] <= commune.money / variables.prices[need[0]]
                      and commune.production_demand[need[0]] <= variables.total_supply[need[0]]):
                    spent = variables.prices[need[0]] * commune.production_demand[need[0]]
                    bought = commune.production_demand[need[0]]

                # Pode comprar <= Demanda & Pode comprar <= Oferta - situação 2, compra tudo o que consegue
                elif (commune.money / variables.prices[need[0]] <= commune.production_demand[need[0]]
                      and commune.money / variables.prices[need[0]] <= variables.total_supply[need[0]]):
                    spent = commune.money
                    bought = round(commune.money / variables.prices[need[0]])

                # O min(demanda, pode comprar) é maior que a oferta - situação 3, compra tudo que há no mercado
                else:
                    spent = variables.prices[need[0]] * variables.total_supply[need[0]]
                    bought = variables.total_supply[need[0]]

                commune.goods[need[0]] += bought
                commune.money -= spent

                variables.communes[need[0]].goods[need[0]] -= bought
                variables.communes[need[0]].money += spent

                variables.total_supply -= bought

        except TypeError:
            pass
