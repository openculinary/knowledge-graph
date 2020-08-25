import argparse
from pathlib import Path
import sys

from web.loader import (
    CACHE_PATHS,
    retrieve_nutrition,
    write_items,
)


parser = argparse.ArgumentParser(description='Generate nutrition data')
parser.add_argument(
    '--nutrition',
    default=CACHE_PATHS['nutrition'],
    help='Cached nutrition file to read/write'
)
parser.add_argument(
    '--update',
    action='store_true',
    help='Update cached content'
)
args = parser.parse_args()

nutrition = list(retrieve_nutrition())

if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        Path(args.nutrition).parent.mkdir(parents=True, exist_ok=True)
        output = open(args.nutrition, 'w')
    write_items(nutrition, output)
    output.close()
