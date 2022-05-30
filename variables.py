from commune import Commune

intake_rate = 50
production_rate = 100  # é o mesmo para todos
from goods import Good

growth_rate = 1.001
needy_migration_rate = 0.005
greedy_migration_rate = 0.02

# o ID dos bens é implícito pela sua posição na lista.
# se não se precisa de outros bens para ser produzido, o terceiro item será None
goods = (
    Good(0, 'Água', None, production_rate=production_rate * 2),
    Good(1, 'Grão', (0,)),
    # Good(2, 'Farinha', (1, )),
    # Good(3, 'Lenha', None),
    # Good(4, 'Pão', (0, 1, 3, )),
)

needs = [
    [(0, 20), (1, 20), ],
    [(0, 65), (4, 25)],
]

# Migrantes que migram porque há lugares melhores para estar
needy_migrants = 0
needy_goods = [0] * len(goods)
needy_money = 0

# Migrantes que migram porque há oportunidades de fazer dinheiro
greedy_migrants = 0
greedy_goods = [0] * len(goods)
greedy_money = 0

money_supply = 0
population = 0

# Define o preço inicial igualmente para todos os bens. O preço inicial não importa contanto que não seja 0.
prices = [1] * len(goods)
total_demand = [0] * len(goods)
total_supply = [0] * len(goods)

# Memórias para fazer migração baseado em oportunidade de ganhos
price_memory = prices[:]
demand_memory = total_demand[:]
supply_memory = total_supply[:]

# ID, tamanho, dinheiro, ID do que produz
# tecnicamente falando, o  ID é implícito pelo bem que produz.

communes = [Commune(100, 99999, 0),
            Commune(100, 99999, 1), ]
