import variables


def emigrate():
    flag = False
    for commune in variables.communes:
        if commune.welfare > 0.5:
            flag = True

    if flag:
        for commune in variables.communes:
            if commune.welfare < 0.5:
                variables.to_migrate += round(commune.size * (commune.welfare / 0.5) * variables.migration_rate)
                commune.size -= round(commune.size * (commune.welfare / 0.5) * variables.migration_rate)

            if commune.size < 0:
                commune.size = 0
                commune.welfare = 0.51


def immigrate():
    havens = []
    total = 0
    for commune in variables.communes:
        if commune.welfare >= 0.5:
            havens.append(commune)
            total += commune.welfare

    if len(havens) > 0:
        total /= len(havens)
        for haven in havens:
            haven.size += round(variables.to_migrate * (haven.welfare / total))
            variables.to_migrate -= round(variables.to_migrate * (haven.welfare / total))
