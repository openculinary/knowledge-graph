import json

from hashedixsearch import (
    tokenize,
)


class Nutrition(object):

    def __init__(self, product, protein, fat, carbohydrates, energy, fibre):
        self.product = product
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates
        self.energy = energy
        self.fibre = fibre

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'product': self.product,
            'protein': self.protein,
            'fat': self.fat,
            'carbohydrates': self.carbohydrates,
            'energy': self.energy,
            'fibre': self.fibre,
        }

    def tokenize(self, stopwords=True, stemmer=True, analyzer=True):
        from web.models.product import Product
        for term in tokenize(doc=self.product, stemmer=Product.stemmer):
            for subterm in term:
                yield subterm
            if len(term) > 1:
                return
