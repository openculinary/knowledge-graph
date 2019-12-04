from ingreedypy import Ingreedy
import json
import re
import requests


def discard(product):
    # Discard rare items
    if product['recipe_count'] < 5:
        return True
    # Discard separator items
    if re.match('[-_]{3}', product['product']):
        return True
    # Discard items with leading quantities
    if re.match('\\d+', product['product']):
        return True
    # Discard items with embedded quantities
    if re.search('[(, /]+\\d+', product['product']):
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
            yield product


def load_product_terms(product):
    pass


if __name__ == '__main__':
    products = retrieve_products(filename='products.json')
    for product in products:
        load_product_terms(product)
        print(f"* Loaded {product['product']}")
