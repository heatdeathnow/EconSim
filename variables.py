from commune import Commune

growth_rate = 1.001
migration_rate = 0.1
intake_rate = 100
production_rate = 200
money_velocity = 5

# o ID dos bens é implícito pela sua posição na lista.
# good = ("Nome", quantidade que comuna tamanho 1 produz, lista com IDs e respectivas quantidades para produzi-lo)
# se não se precisa de outros bens para ser produzido, o terceiro item será None
goods = (("Água", None),
         ("Grão", ((0, intake_rate * 2), )),
         # ("Farinha", ((1, intake_rate * 2), )),
         # ("Lenha", None),
         # ("Pão", ((0, intake_rate / 2), (1, intake_rate / 2), (3, intake_rate))),
         )

needs = [[(0, 80), (1, 40), ],
         [(0, 85), (4, 40)],
         ]

to_migrate = 0
migrant_goods = [0] * len(goods)
migrant_money = 0

money_supply = 0
population = 0

total_demand = [0] * len(goods)
total_supply = [0] * len(goods)
prices = [0] * len(goods)

# ID, tamanho, dinheiro, ID do que produz
# tecnicamente falando, o  ID é implícito pelo bem que produz.

communes = [Commune(100, 99999, 0),
            Commune(100, 99999, 1), ]
