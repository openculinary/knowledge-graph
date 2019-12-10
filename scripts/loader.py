import json
from pymmh3 import hash_bytes
import re
import requests

from ingreedypy import Ingreedy

from scripts.product_tree import ProductGraph


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
            product['id'] = hash_bytes(product['product'])
            yield product


def print_subtree(product, level=0, path=None):
    print(product['product'])

    path = path or []
    for child_id in product['children']:
        child = graph.products_by_id[child_id]
        if child['primary_parent'] == product and child_id not in path:
            print(f" {'  ' * level}\\-- ", end='')
            path.append(child_id)
            print_subtree(child, level + 1, path)


if __name__ == '__main__':
    products = retrieve_products(filename='products.json')
    graph = ProductGraph(products)
    for product_id, product in graph.products_by_id.items():
        if product['depth'] == 0:
            print_subtree(product)
