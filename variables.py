from commune import Commune

growth_rate = 1.001
migration_rate = 1.001

# o ID dos bens é implícito pela sua posição na lista.
# good = ("Nome", quantidade que comuna tamanho 1 produz, lista com IDs e respectivas quantidades para produzi-lo)
# se não se precisa de outros bens para ser produzido, o terceiro item será None
goods = (("Água", 100000000, None),
         ("Grão", 15000, ((0, 75000), ))
         , )

to_migrate = 0
money_supply = 0

total_demand = [0] * len(goods)
total_supply = [0] * len(goods)
prices = [0] * len(goods)

# ID, tamanho, dinheiro, ID do que produz
# tecnicamente falando, o  ID é implícito pelo bem que produz.

communes = [Commune(100, 99999999, 0),
            Commune(100, 99999999, 1), ]
