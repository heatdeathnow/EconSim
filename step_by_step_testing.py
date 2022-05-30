import market
import migration
import variables

while True:

    print(f'1 - atualizar')
    print(f'2 - consumir')
    print(f'3 - produzir')
    print(f'4 - crescer')
    print(f'5 - migrar')
    print(f'6 - trocar')
    print(f'7 - memorizar')
    choice = int(input('> '))

    if choice == 1:
        for commune in variables.communes:
            commune.assess()
        market.assess()

    elif choice == 2:
        for commune in variables.communes:
            commune.consume()

    elif choice == 3:
        for commune in variables.communes:
            commune.produce()

    elif choice == 4:
        for commune in variables.communes:
            commune.grow()

    elif choice == 5:
        migration.migrate()

    elif choice == 6:
        market.exchange()

    elif choice == 7:
        market.record()

    print()
    print('=' * 10 + ' MERCADO ' + '=' * 10)
    print()
    print(f'Base monetária: {variables.money_supply:.2f}')
    print(f'População: {variables.population}')
    print()
    for count in range(len(variables.goods)):
        print(f'Demanda de {variables.goods[count].name}: {variables.total_demand[count]}')
        print(f'Oferta de {variables.goods[count].name}: {variables.total_supply[count]}')
        print(f'Preço de {variables.goods[count].name}: {variables.prices[count] / 100:.2f}')
        print()

    print()
    print('=' * 10 + ' COMUNAS ' + '=' * 10)
    print()
    for commune in variables.communes:
        print(f'Comuna #{commune.produces}')

        print()
        for count in range(len(variables.goods)):
            print(f'Quantidade de {variables.goods[count].name}: {commune.goods[count]}')

        print()
        for count in range(len(variables.goods)):
            print(f'Demanda essencial de {variables.goods[count].name}: {commune.survival_demand[count]}')

        print()
        for count in range(len(variables.goods)):
            print(f'Demanda produtiva de {variables.goods[count].name}: {commune.production_demand[count]}')

        print()
        for count in range(len(variables.goods)):
            print(f'Demanda agregada de {variables.goods[count].name}: {commune.total_demand[count]}')

        print()
        print(f'População: {commune.size}')
        print(f'Dinheiro: {commune.money:.2f}')
        print(f'Bem-estar: {commune.welfare}')
        print(f'Compensação: {commune.compensation}')
        print()
