import argparse
from pathlib import Path
import sys

from web.loader import (
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

if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        Path(args.products).parent.mkdir(parents=True, exist_ok=True)
        output = open(args.products, 'w')
    write_items(products, output)
    output.close()
