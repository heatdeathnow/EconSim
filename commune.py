import variables
import math


class Commune:
    def __init__(self, size, money, produces):
        self.goods = [0] * len(variables.goods)
        self.survival_demand = [0] * len(variables.goods)
        self.production_demand = [0] * len(variables.goods)
        self.total_demand = [0] * len(variables.goods)

        self.welfare = 0.5
        self.size = size
        self.money = money
        self.produces = produces

        # (ID do bem, quantidade necessária para uma comuna de tamanho 1)
        self.needs = variables.needs[0]
        self.compensation = 1  # Número entre 0 e 1 que multiplica a produção baseado na movimentação dos estoques.

    def assess(self):

        # Toda oferta
        for count in range(len(variables.goods)):
            self.total_demand[count] = -self.goods[count]

        # Toda oferta descontada do que precisa para sobreviver
        for need in self.needs:

            # Não se pode ter demanda essencial pelo que produz. (consequentemente não se pode ter demanda produtiva
            # pelo que produz já que nada leva a si mesmo para ser produzido.)
            if need[0] == self.produces:
                self.survival_demand[need[0]] = 0
                self.total_demand[need[0]] = -self.goods[need[0]]  # isso não é um problema se o consumo é feito antes.

            else:
                self.survival_demand[need[0]] = (need[1] * self.size) - self.goods[need[0]]
                self.total_demand[need[0]] += need[1] * self.size

                if self.survival_demand[need[0]] < 0:
                    self.survival_demand[need[0]] = 0

        # Oferta descontada do que precisa para sobreviver descontada do que precisa para produzir
        try:
            for need in variables.goods[self.produces].recipe:
                self.production_demand[need] = ((variables.goods[self.produces].intake_rate * self.size)
                                                - self.goods[need])
                self.total_demand[need] += variables.goods[self.produces].intake_rate * self.size

                if self.production_demand[need] < 0:
                    self.production_demand[need] = 0

        except TypeError:
            pass

    def produce(self):
        try:
            if variables.goods[self.produces].recipe is None:
                self.goods[self.produces] += (variables.goods[self.produces].production_rate
                                              * self.size * self.compensation)
                self.goods[self.produces] = round(self.goods[self.produces])

            else:
                lowest_proportion = 1
                for need in variables.goods[self.produces].recipe:
                    if (self.goods[need] / (variables.goods[self.produces].intake_rate * self.size * self.compensation)
                            < lowest_proportion):
                        lowest_proportion = (self.goods[need] / (variables.goods[self.produces].intake_rate
                                                                 * self.size * self.compensation))

                # adiciona os bens produzidos ao inventário
                self.goods[self.produces] += (variables.goods[self.produces].production_rate * self.size
                                              * lowest_proportion * self.compensation)
                self.goods[self.produces] = round(self.goods[self.produces])

                # Retira o que foi usado na produção
                for need in variables.goods[self.produces].recipe:
                    self.goods[need] -= (variables.goods[self.produces].intake_rate * self.size
                                         * lowest_proportion * self.compensation)
                    self.goods[need] = round(self.goods[need])

        except ZeroDivisionError:
            pass

    def consume(self):
        mean = 0
        try:  # para caso população = 0

            save = 1
            for need in self.needs:

                try:

                    # Se o bem que vai consumir também é necessário para produção e se tem menos do que o necessário
                    # para os dois...
                    if (need[0] in variables.goods[self.produces].recipe
                            and (need[1] + variables.goods[self.produces].intake_rate) * self.size > self.goods[
                                need[0]]):
                        # Ele vai consumir: menor(metade do que tem, metade do que consome)
                        mean += min(math.ceil(need[1] * self.size / 2),
                                    math.ceil(self.goods[need[0]] / 2)) / (need[1] * self.size)
                        self.goods[need[0]] -= min(math.ceil(need[1] * self.size / 2),
                                                   math.ceil(self.goods[need[0]] / 2))

                    # Se o que você vai consumir é o que você produz e você vai consumir tudo...
                    elif need[0] == self.produces and need[1] * self.size >= self.goods[need[0]]:
                        # Consome apenas metade do que tem
                        mean += (self.goods[need[0]] / 2) / (need[1] * self.size)
                        self.goods[need[0]] -= math.floor(self.goods[need[0]] / 2)

                    elif self.goods[need[0]] < (need[1] * self.size):
                        mean += self.goods[need[0]] / (need[1] * self.size)
                        self.goods[need[0]] = 0

                    else:
                        self.goods[need[0]] -= need[1] * self.size
                        mean += 1

                except TypeError:
                    if self.goods[need[0]] < (need[1] * self.size):
                        mean += self.goods[need[0]] / (need[1] * self.size)
                        self.goods[need[0]] = 0

                    else:
                        self.goods[need[0]] -= need[1] * self.size
                        mean += 1

            mean /= len(self.needs)

            if round(mean, 1) >= 0.5 and self.welfare < 0.25:
                self.welfare += mean / 10
            elif mean > 0.55:
                self.welfare += (mean - 0.55) / 5
            else:
                self.welfare -= (0.55 - mean) / 5

            if self.welfare > 1:
                self.welfare = 1
            elif self.welfare < 0:
                self.welfare = 0

        except ZeroDivisionError:
            pass

    def grow(self):

        if self.welfare >= 0.75:
            self.size *= variables.growth_rate
            self.size = math.ceil(self.size)
        elif self.welfare <= 0.25:
            self.size /= variables.growth_rate
            self.size = math.floor(self.size)

        if self.size <= 0:
            self.size = 0
            self.welfare = 0.5
            self.goods = [0] * len(variables.goods)
