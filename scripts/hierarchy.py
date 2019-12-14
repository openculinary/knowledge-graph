import argparse
import sys

from web.loader import (
    CACHE_PATHS,
    retrieve_products,
    retrieve_stopwords,
    write_items,
)
from web.models.product_graph import ProductGraph


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
stopwords = retrieve_stopwords(args.stopwords)

graph = ProductGraph(products, stopwords)
products = graph.filter_products()
stopwords = graph.filter_stopwords()

graph = ProductGraph(products, stopwords)
graph.generate_hierarchy()
graph.filter_products()


def node_explorer(graph, node, path):
    for child_id in node.children:
        if child_id in path:
            continue
        child = graph.products_by_id[child_id]
        if child.parent_id == node.id:
            yield child
            for child in node_explorer(graph, child, path + [child_id]):
                yield child


def graph_explorer(graph):
    for root in graph.roots:
        yield root
        for node in node_explorer(graph, root, [root.id]):
            yield node


if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        output = open(args.hierarchy, 'w')
    write_items(graph_explorer(graph), output)
    output.close()
