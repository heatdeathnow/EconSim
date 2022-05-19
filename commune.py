import variables


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
        self.needs = [(0, 17000), (1, 6000), ]

    def assess(self):

        # Toda oferta
        for count in range(len(variables.goods)):
            self.total_demand[count] = -self.goods[count]

        # Toda oferta descontada do que precisa para sobreviver
        for need in self.needs:
            self.total_demand[need[0]] += need[1] * self.size
            self.survival_demand[need[0]] = need[1] * self.size

        # Oferta descontada do que precisa para sobreviver descontada do que precisa para produzir
        try:
            for need in variables.goods[self.produces][2]:
                self.total_demand[need[0]] += need[1] * self.size
                self.production_demand[need[0]] = need[1] * self.size

        except TypeError:
            pass

    def produce(self):
        try:
            if variables.goods[self.produces][2] is None:
                self.goods[self.produces] += variables.goods[self.produces][1] * self.size

            else:
                lowest_proportion = 1
                for need in variables.goods[self.produces][2]:
                    if self.goods[need[0]] / (need[1] * self.size) < lowest_proportion:
                        lowest_proportion = self.goods[need[0]] / (need[1] * self.size)

                # adiciona os bens produzidos ao inventário
                self.goods[self.produces] += variables.goods[self.produces][1] * self.size * lowest_proportion
                self.goods[self.produces] = round(self.goods[self.produces])

                # Retira o que foi usado na produção
                for need in variables.goods[self.produces][2]:
                    self.goods[need[0]] -= need[1] * self.size * lowest_proportion
                    self.goods[need[0]] = round(self.goods[need[0]])

        except ZeroDivisionError:
            pass

    def consume(self):
        mean = 0
        try:
            for need in self.needs:
                if self.goods[need[0]] < (need[1] * self.size):
                    mean += self.goods[need[0]] / (need[1] * self.size)
                    self.goods[need[0]] = 0

                else:
                    self.goods[need[0]] -= need[1] * self.size
                    mean += 1

            mean /= len(self.needs)
            self.welfare *= (0.35 + mean)

            if self.welfare > 1:
                self.welfare = 1

        except ZeroDivisionError:
            pass

    def grow(self):

        if self.welfare >= 0.75:
            self.size *= (variables.growth_rate * 1.25)
        elif 0.75 > self.welfare >= 0.5:
            self.size *= variables.growth_rate
        elif 0.5 > self.welfare >= 0.25:
            self.size /= variables.growth_rate
        else:
            self.size /= (variables.growth_rate * 1.25)

        self.size = round(self.size)

        if self.size < 0:
            self.size = 0
            self.welfare = 0.51

        if self.size == 0:
            self.goods = [0] * len(variables.goods)
