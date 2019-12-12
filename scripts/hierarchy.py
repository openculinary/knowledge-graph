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
    default=CACHE_PATHS['hierarchy'],
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

graph = ProductGraph(products)
products = graph.filter_products()
stopwords = retrieve_stopwords(args.stopwords)

graph = ProductGraph(products, stopwords)
graph.generate_hierarchy()


def node_explorer(graph, node):
    yield node
    for child_id in node.children:
        child = graph.products_by_id[child_id]
        if not child.primary_parent == node:
            continue
        yield child
        for node in node_explorer(graph, child):
            yield node


def graph_explorer(graph):
    for root in graph.roots:
        for node in node_explorer(graph, root):
            yield node


output = sys.stdout
if args.update:
    output = open(args.hierarchy, 'w')
write_items(graph_explorer(graph), output)
output.close()
