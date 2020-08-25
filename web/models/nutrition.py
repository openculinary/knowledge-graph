import json


class Nutrition(object):

    def __init__(self, product, protein, fat, carbohydrates, energy, fibre):
        self.product = product
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates
        self.energy = energy
        self.fibre = fibre

    def __repr__(self):
        return json.dumps({
            'product': self.product,
            'protein': self.protein,
            'fat': self.fat,
            'carbohydrates': self.carbohydrates,
            'energy': self.energy,
            'fibre': self.fibre,
        })
