import variables


class Good:
    def __init__(self, id, name, recipe, production_rate=variables.production_rate, intake_rate=variables.intake_rate):

        self.id = id
        self.name = name
        self.production_rate = production_rate
        self.intake_rate = intake_rate

        # (id, id, id, id..., )
        self.recipe = recipe
