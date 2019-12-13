from flask import Flask, Response

from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
)
from web.models.product_graph import ProductGraph

app = Flask(__name__)

filename = CACHE_PATHS['hierarchy']
hierarchy = retrieve_hierarchy(filename)
graph = ProductGraph(hierarchy)


# Custom streaming method
def stream(items):
    for item in items:
        yield f'{item}\n'


@app.route('/ingredients/hierarchy')
def hierarchy():
    products = graph.filter_products()
    return Response(stream(products), content_type='application/x-ndjson')
