import variables
import math


def migrate():

    # Emigração para melhores oportunidades de adquirir bens.
    mean = 0
    for commune in variables.communes:
        mean += commune.welfare
    mean /= len(variables.communes)

    for commune in variables.communes:
        if commune.welfare < mean:

            # Dinheiro * (Migrantes / Total) simplificado
            variables.needy_money += math.ceil(commune.money * variables.needy_migration_rate)
            commune.money -= math.ceil(commune.money * variables.needy_migration_rate)

            for count in range(len(variables.goods)):
                variables.needy_goods[count] += math.ceil(commune.goods[count] * variables.needy_migration_rate)
                commune.goods[count] -= math.ceil(commune.goods[count] * variables.needy_migration_rate)

            variables.needy_migrants += math.ceil(commune.size * variables.needy_migration_rate)
            commune.size -= math.ceil(commune.size * variables.needy_migration_rate)

        if commune.size <= 0:
            commune.size = 0
            commune.welfare = 0.5
            commune.goods = [0] * len(variables.goods)

    # Emigração oportunista
    opportunities = 0
    for count in range(0, len(variables.demand_memory)):
        if variables.demand_memory[count] > variables.supply_memory[count]:
            opportunities += 1

    if opportunities > 0:
        for commune in variables.communes:
            if variables.demand_memory[commune.produces] <= variables.supply_memory[commune.produces]:
                variables.greedy_money += math.ceil(commune.money * variables.greedy_migration_rate)
                commune.money -= math.ceil(commune.money * variables.greedy_migration_rate)

                for count in range(len(variables.goods)):
                    variables.greedy_goods[count] += math.ceil(commune.goods[count] * variables.greedy_migration_rate)
                    commune.goods[count] -= math.ceil(commune.goods[count] * variables.greedy_migration_rate)

                variables.greedy_migrants += math.ceil(commune.size * variables.greedy_migration_rate)
                commune.size -= math.ceil(commune.size * variables.greedy_migration_rate)

    # Imigração carente
    havens = 0
    for commune in variables.communes:
        if commune.welfare > mean:
            havens += 1

    for commune in variables.communes:
        if commune.welfare > mean:
            commune.money += math.ceil(variables.needy_money / havens)
            variables.needy_money -= math.ceil(variables.needy_money / havens)

            for count in range(len(variables.goods)):
                commune.goods[count] += math.ceil(variables.needy_goods[count] / havens)
                variables.needy_goods[count] -= math.ceil(variables.needy_goods[count] / havens)

            commune.size += math.ceil(variables.needy_migrants / havens)
            variables.needy_migrants -= math.ceil(variables.needy_migrants / havens)

    # Imigração oportunista
    for commune in variables.communes:
        if variables.demand_memory[commune.produces] > variables.supply_memory[commune.produces]:
            commune.money += math.ceil(variables.greedy_money / opportunities)
            variables.greedy_money -= math.ceil(variables.greedy_money / opportunities)

            for count in range(len(variables.goods)):
                commune.goods[count] += math.ceil(variables.greedy_goods[count] / opportunities)
                variables.greedy_goods[count] -= math.ceil(variables.greedy_goods[count] / opportunities)

            commune.size += math.ceil(variables.greedy_migrants / opportunities)
            variables.greedy_migrants -= math.ceil(variables.greedy_migrants / opportunities)
