class Nutrition(object):

    def __init__(self, protein, fat, carbohydrates, energy, fibre):
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates
        self.energy = energy
        self.fibre = fibre

    def to_dict(self):
        return {
            'protein': self.protein,
            'fat': self.fat,
            'carbohydrates': self.carbohydrates,
            'energy': self.energy,
            'fibre': self.fibre,
        }
