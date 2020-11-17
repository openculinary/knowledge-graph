import json
import os

from web.models.product import Product


CACHE_PATHS = {
    'hierarchy': 'web/data/generated/hierarchy.json',
    'stopwords': 'web/data/generated/stopwords.txt',
    'appliance_queries': 'web/data/equipment/appliances.txt',
    'utensil_queries': 'web/data/equipment/utensils.txt',
    'vessel_queries': 'web/data/equipment/vessels.txt',
}


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]


def retrieve_stopwords(filename):
    if not os.path.exists(filename):
        raise RuntimeError(f'Could not read stopwords from: {filename}')

    print(f'Reading stopwords from {filename}')
    with open(filename) as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            yield line.strip()


def retrieve_hierarchy(filename):
    if not os.path.exists(filename):
        raise RuntimeError(f'Could not read hierarchy from: {filename}')

    print(f'Reading hierarchy from {filename}')
    with open(filename) as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            product = json.loads(line)
            yield Product(
                id=product['id'],
                name=product['product'],
                frequency=product['recipe_count'],
                parent_id=product.get('parent_id'),
                nutrition=product.get('nutrition')
            )
