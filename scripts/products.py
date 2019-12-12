import argparse
import sys

from scripts.loader import (
    CACHE_PATHS,
    retrieve_products,
    write_items,
)


parser = argparse.ArgumentParser(description='Generate product data')
parser.add_argument(
    '--products',
    default=CACHE_PATHS['products'],
    help='Cached products file to read/write'
)
parser.add_argument(
    '--update',
    action='store_true',
    help='Update cached content'
)
args = parser.parse_args()

products = list(retrieve_products(args.products))

output = sys.stdout
if args.update:
    output = open(args.products, 'w')
write_items(products, output)
output.close()
