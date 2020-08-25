import json
import os
import re
import requests

from ingreedypy import Ingreedy

from web.models.nutrition import Nutrition
from web.models.product import Product


CACHE_PATHS = {
    'hierarchy': 'web/data/generated/hierarchy.json',
    'products': 'web/data/generated/ingredients.json',
    'stopwords': 'web/data/generated/stopwords.txt',
    'appliance_queries': 'web/data/equipment/appliances.txt',
    'utensil_queries': 'web/data/equipment/utensils.txt',
    'vessel_queries': 'web/data/equipment/vessels.txt',
}

NUTRITION_PATHS = {
    'lookup': 'web/data/external/ingreedy-data/data/processed/foodmap.json',
    'mccance': 'web/data/external/ingreedy-data/data/processed/mccance.json',
    'usfdc': 'web/data/external/ingreedy-data/data/processed/usfdc.json',
}


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]


def discard(product):
    # Discard rare items
    if product['recipe_count'] < 5:
        return True
    # Discard separator items
    if re.match('[-_]+', product['product']):
        return True
    # Discard items with leading quantities
    if re.match('\\d+', product['product']):
        return True
    # Discard items with embedded quantities
    if re.search('[(, /]+\\d+', product['product']):
        return True
    # Products must contain at least three-letter word terms
    if not re.search('\\S{3}', product['product']):
        return True
    # Drop 'container' items
    if product['product'].endswith(':'):
        return True
    return False


def prefilter(name):

    # Remove text enclosed by parentheses
    open_parens = name.find('(')
    close_parens = name.rfind(')')
    if open_parens > 0 and close_parens > open_parens:
        name = name[:open_parens - 1] + name[close_parens + 1:]

    # Attempt ingreedy-py parsing; drop quantity-related text on success
    try:
        parse = Ingreedy().parse(name)
        return parse['ingredient']
    except Exception:
        return name


def retrieve_products(filename):
    if os.path.exists(filename):
        print(f'Reading products from: {filename}')
        recipe_file = open(filename, 'r')
        reader = recipe_file.readlines
    else:
        print('Streaming product data from api')
        reader = requests.get(
            url='http://localhost/products',
            stream=True,
            proxies={}
        ).iter_lines

    count = 0
    for line in reader():
        count += 1
        if count % 1000 == 0:
            print(f'- {count} products loaded')

        line = line.decode() if isinstance(line, bytes) else line
        if line.startswith('#'):
            continue

        product = json.loads(line)
        if discard(product):
            continue

        yield Product(
            name=prefilter(product['product']),
            frequency=product['recipe_count']
        )
    print(f'- {count} products loaded')


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
                name=product['product'],
                frequency=product['recipe_count'],
                parent_id=product.get('parent_id')
            )


def retrieve_nutrition():
    lookup = NUTRITION_PATHS['lookup']
    if not os.path.exists(lookup):
        raise RuntimeError(f'Could not read nutrition lookup from: {lookup}')
    with open(lookup) as f:
        lookup = json.loads(f.read())

    mccance = NUTRITION_PATHS['mccance']
    if not os.path.exists(mccance):
        raise RuntimeError(f'Could not read mccance nutrition from: {mccance}')
    with open(mccance) as f:
        mccance = json.loads(f.read())
        mccance = {item["name"]: item for item in mccance}

    usfdc = NUTRITION_PATHS['usfdc']
    if not os.path.exists(usfdc):
        raise RuntimeError(f'Could not read usfdc nutrition from: {usfdc}')
    with open(usfdc) as f:
        usfdc = json.loads(f.read())
        usfdc = {item["name"]: item for item in usfdc}

    for metadata in lookup:
        nutrition = None
        product = metadata["normalized_name"]
        datasets = {"food": mccance, "food_usfdc": usfdc}
        for key, dataset in datasets.items():
            name = metadata[key]
            if name and name in dataset:
                nutrition = dataset[name]
                break
        if not nutrition:
            continue
        yield Nutrition(
            product=product,
            fat=nutrition["fat"],
            protein=nutrition["protein"],
            carbohydrates=nutrition["carbs"],
            energy=nutrition["energy"],
            fibre=nutrition["fibre"],
        )


def write_items(items, output):
    output.write('# Autogenerated; do not edit\n')
    for item in items:
        output.write(f'{item}\n')
