import argparse
import sys

from scripts.loader import (
    CACHE_PATHS,
    retrieve_products,
    retrieve_stopwords,
    write_items,
)
from scripts.models.product_graph import ProductGraph


parser = argparse.ArgumentParser(description='Generate product hierarchies')
parser.add_argument(
    '--hierarchy',
    help='Cached hierarchy file to read/write'
)
parser.add_argument(
    '--products',
    default=CACHE_PATHS['products'],
    help='Cached products file to read/write'
)
parser.add_argument(
    '--stopwords',
    default=CACHE_PATHS['stopwords'],
    help='Cached stopwords file to read/write'
)
parser.add_argument(
    '--update',
    action='store_true',
    help='Update cached content'
)
args = parser.parse_args()

products = retrieve_products(args.products)
stopwords = retrieve_stopwords(args.stopwords)

graph = ProductGraph(products, stopwords)
products = graph.filtered_products()

graph = ProductGraph(products, stopwords)
roots = graph.generate_hierarchy()

output = sys.stdout
if args.update:
    output = open(args.products)
write_items(roots, output)
output.close()
