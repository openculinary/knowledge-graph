from ingreedypy import Ingreedy
import json
import re
import requests

from scripts.search import (
    add_to_search_index,
    build_search_index,
    execute_queries,
)


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

    # Discard full ingredient descriptions
    try:
        parsed = Ingreedy().parse(product['product'])
        if parsed.get('amount') or parsed.get('unit'):
            return True
    except Exception:
        pass

    return False


def retrieve_products(filename=None):
    if filename:
        recipe_file = open(filename, 'r')
        reader = recipe_file.readlines
    else:
        headers = {'Host': 'api'}
        url = 'http://192.168.0.23:30080/api/products'
        reader = requests.get(url, headers=headers, stream=True).iter_lines

    for line in reader():
        product = json.loads(line)
        if not discard(product):
            yield product['product']


def find_related_products(index, product):
    results = execute_queries(index, [product])
    children = results.keys()
    return set(children)


if __name__ == '__main__':
    index = build_search_index()

    products_by_id = {}
    products = retrieve_products(filename='products.json')
    for product_id, product in enumerate(products):
        products_by_id[product_id] = {'id': product_id, 'product': product}
        add_to_search_index(index, product_id, product)

    for product_id, product in products_by_id.items():
        related = find_related_products(index, product['product'])
        related.remove(product_id)

        for related_id in related:
            products_by_id[related_id]['parent'] = product_id

        print(product)
