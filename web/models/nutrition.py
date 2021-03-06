class Nutrition(object):

    def __init__(
        self,
        protein,
        protein_units,
        fat,
        fat_units,
        carbohydrates,
        carbohydrates_units,
        energy,
        energy_units,
        fibre,
        fibre_units,
    ):
        self.protein = protein
        self.protein_units = protein_units
        self.fat = fat
        self.fat_units = fat_units
        self.carbohydrates = carbohydrates
        self.carbohydrates_units = carbohydrates_units
        self.energy_units = energy_units
        self.fibre_units = fibre_units

    def to_dict(self):
        return {
            'protein': self.protein,
            'protein_units': self.protein_units,
            'fat': self.fat,
            'fat_units': self.fat_units,
            'carbohydrates_units': self.carbohydrates_units,
            'energy_units': self.energy_units,
            'fibre_units': self.fibre_units,
        }
