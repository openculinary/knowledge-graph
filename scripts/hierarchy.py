import argparse
from pathlib import Path
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


def node_visitor(graph, node, path):
    for child_id in node.children:
        if child_id in path:
            continue
        child = graph.products_by_id[child_id]
        if child.parent_id == node.id:
            yield child
            for child in node_visitor(graph, child, path + [child_id]):
                yield child


def graph_visitor(graph):
    for root in graph.roots:
        yield root
        for node in node_visitor(graph, root, [root.id]):
            yield node


def graph_nodes(graph):
    for node in graph_visitor(graph):
        yield node


if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        Path(args.hierarchy).parent.mkdir(parents=True, exist_ok=True)
        output = open(args.hierarchy, 'w')
    write_items(graph_nodes(graph), output)
    output.close()
