import market
import migration
import variables

while True:

    print(f'1 - atualizar')
    print(f'2 - consumir')
    print(f'3 - produzir')
    print(f'4 - crescer')
    print(f'5 - emigrar')
    print(f'6 - imigrar')
    print(f'7 - trocar')
    choice = int(input('> '))

    if choice == 1:
        for commune in variables.communes:
            commune.assess()
        market.assess()

    if choice == 2:
        for commune in variables.communes:
            commune.consume()

    if choice == 3:
        for commune in variables.communes:
            commune.produce()

    if choice == 4:
        for commune in variables.communes:
            commune.grow()

    if choice == 5:
        migration.emigrate()

    if choice == 6:
        migration.immigrate()

    if choice == 7:
        market.exchange()

    print()
    print('=' * 10 + ' MERCADO ' + '=' * 10)
    print()
    print(f'Base monetária: {variables.money_supply:.2f}')
    for count in range(len(variables.goods)):
        print(f'Demanda de {variables.goods[count][0]}: {variables.total_demand[count]}')
        print(f'Oferta de {variables.goods[count][0]}: {variables.total_supply[count]}')
        print(f'Preço de {variables.goods[count][0]}: {variables.prices[count]}')
        print()

    print()
    print('=' * 10 + ' COMUNAS ' + '=' * 10)
    print()
    for commune in variables.communes:
        print(f'Comuna #{commune.produces}')

        print()
        for count in range(len(variables.goods)):
            print(f'Quantidade de {variables.goods[count][0]}: {commune.goods[count]}')

        print()
        for count in range(len(variables.goods)):
            print(f'Demanda essencial de {variables.goods[count][0]}: {commune.survival_demand[count]}')

        print()
        for count in range(len(variables.goods)):
            print(f'Demanda produtiva de {variables.goods[count][0]}: {commune.production_demand[count]}')

        print()
        for count in range(len(variables.goods)):
            print(f'Demanda agregada de {variables.goods[count][0]}: {commune.total_demand[count]}')

        print()
        print(f'População: {commune.size}')
        print(f'Dinheiro: {commune.money:.2f}')
        print(f'Bem-estar: {commune.welfare}')
        print()
