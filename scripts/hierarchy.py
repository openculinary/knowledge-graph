import argparse
from pathlib import Path
import sys

from web.loader import (
    CACHE_PATHS,
    retrieve_products,
    retrieve_nutrition,
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
    '--nutrition',
    default=CACHE_PATHS['nutrition'],
    help='Cached nutrition file to read/write'
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
nutrition = retrieve_nutrition(args.nutrition)
stopwords = retrieve_stopwords(args.stopwords)

graph = ProductGraph(products, stopwords)
products = graph.filter_products()
stopwords = graph.filter_stopwords()

graph = ProductGraph(products, stopwords, nutrition)
graph.generate_hierarchy()
graph.filter_products()


def node_nutrition(graph, node):
    if node.nutrition_key:
        return graph.nutrition_by_key[node.nutrition_key]
    elif node.parent_id:
        return node_nutrition(graph, graph.products_by_id[node.parent_id])


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
        root.nutrition = node_nutrition(graph, root)
        yield root
        for node in node_explorer(graph, root, [root.id]):
            node.nutrition = node_nutrition(graph, node)
            yield node


if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        Path(args.hierarchy).parent.mkdir(parents=True, exist_ok=True)
        output = open(args.hierarchy, 'w')
    write_items(graph_explorer(graph), output)
    output.close()
