import json
import os
import re
import requests

from ingreedypy import Ingreedy

from scripts.models.product import Product


CACHE_PATHS = {
    'hierarchy': 'scripts/data/generated/hierarchy.json',
    'products': 'scripts/data/generated/ingredients.json',
    'stopwords': 'scripts/data/generated/stopwords.txt',
}


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


def retrieve_products(filename):
    if os.path.exists(filename):
        print(f'Reading products from: {filename}')
        recipe_file = open(filename, 'r')
        reader = recipe_file.readlines
    else:
        url = 'http://192.168.0.23:30080/api/products'
        print(f'Streaming product data from: {url}')
        headers = {'Host': 'api'}
        reader = requests.get(url, headers=headers, stream=True).iter_lines

    count = 0
    ingreedy = Ingreedy()
    for line in reader():
        count += 1
        if count % 1000 == 0:
            print(f'- {count} products loaded')

        product = json.loads(line)
        if discard(product):
            continue
        try:
            parse = ingreedy.parse(product['product'])
        except Exception:
            continue
        yield Product(
            name=parse['ingredient'] or product['product'],
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


def write_items(items, output):
    output.write('# Autogenerated; do not edit\n')
    for item in items:
        output.write(f'{item}\n')
