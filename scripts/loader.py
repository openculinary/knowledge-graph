import json
import re
import requests

from scripts.product import Product
from scripts.product_graph import ProductGraph


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
            yield Product(
                name=product['product'],
                frequency=product['recipe_count']
            )


def print_subtree(product, level=0, path=None):
    print(product.name + (' *' if product.stopwords else ''))

    path = path or []
    for child_id in product.children:
        child = graph.products_by_id[child_id]
        if child.primary_parent == product and child_id not in path:
            print(f" {'  ' * level}\\-- ", end='')
            path.append(child_id)
            print_subtree(child, level + 1, path)


if __name__ == '__main__':
    products = retrieve_products(filename='products.json')
    graph = ProductGraph(products)
    for product_id, product in graph.products_by_id.items():
        if product.depth == 0:
            print_subtree(product)
