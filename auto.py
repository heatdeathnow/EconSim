import market
import migration
import commune
import variables

size0 = int(input('População da Comuna 0 > '))
size1 = int(input('População da Comuna 1 > '))
money0 = int(input('Dinheiro da Comuna 0 > '))
money1 = int(input('Dinheiro da Comuna 1 > '))

variables.communes = [commune.Commune(size0, money0, 0),
                      commune.Commune(size1, money1, 1), ]


def gui():
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


while True:

    migration.migrate()

    for commune in variables.communes:
        commune.consume()
        commune.produce()
        commune.grow()
        commune.assess()

    market.assess()
    market.record()
    gui()
    market.exchange()

    for commune in variables.communes:
        commune.assess()
    market.assess()
    gui()
