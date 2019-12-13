import argparse
import sys

from scripts.loader import (
    CACHE_PATHS,
    retrieve_products,
    retrieve_stopwords,
    write_items,
)
from scripts.models.product_graph import ProductGraph


parser = argparse.ArgumentParser(description='Generate stopwords')
parser.add_argument(
    '--products',
    default=CACHE_PATHS['products'],
    help='Cached products file to read from'
)
parser.add_argument(
    '--stopwords',
    default=CACHE_PATHS['stopwords'],
    help='Cached stopwords file to read from'
)
parser.add_argument(
    '--update',
    action='store_true',
    help='Update cached content'
)
args = parser.parse_args()

stopwords = retrieve_stopwords(args.stopwords)
if not stopwords:
    products = retrieve_products(args.products)
    graph = ProductGraph(products)
    stopwords = graph.get_stopwords()

if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        output = open(args.stopwords, 'w')
    write_items(stopwords, output)
    output.close()
