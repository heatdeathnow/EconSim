import variables
import math


def emigrate():
    mean = 0
    for commune in variables.communes:
        mean += commune.welfare
    mean /= len(variables.communes)

    for commune in variables.communes:
        if commune.welfare < mean:

            # Dinheiro * (Migrantes / Total) simplificado
            variables.migrant_money += math.ceil(commune.money * variables.migration_rate)
            commune.money -= math.ceil(commune.money * variables.migration_rate)

            for count in range(len(variables.goods)):
                variables.migrant_goods[count] += math.ceil(commune.goods[count] * variables.migration_rate)
                commune.goods[count] -= math.ceil(commune.goods[count] * variables.migration_rate)

            variables.to_migrate += math.ceil(commune.size * variables.migration_rate)
            commune.size -= math.ceil(commune.size * variables.migration_rate)

        if commune.size <= 0:
            commune.size = 0
            commune.welfare = 0.5
            commune.goods = [0] * len(variables.goods)


def immigrate():
    mean = 0
    havens = 0
    for commune in variables.communes:
        mean += commune.welfare
    mean /= len(variables.communes)

    for commune in variables.communes:
        if commune.welfare > mean:
            havens += 1

    for commune in variables.communes:
        if commune.welfare > mean:
            commune.money += math.ceil(variables.migrant_money / havens)
            variables.migrant_money -= math.ceil(variables.migrant_money / havens)

            for count in range(len(variables.goods)):
                commune.goods[count] += math.ceil(variables.migrant_goods[count] / havens)
                variables.migrant_goods[count] -= math.ceil(variables.migrant_goods[count] / havens)

            commune.size += math.ceil(variables.to_migrate / havens)
            variables.to_migrate -= math.ceil(variables.to_migrate / havens)
