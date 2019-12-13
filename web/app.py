from flask import Flask, jsonify, request, Response

from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
    retrieve_stopwords,
)
from web.models.product_graph import ProductGraph
from web.search import execute_queries

app = Flask(__name__)

filename = CACHE_PATHS['hierarchy']
hierarchy = retrieve_hierarchy(filename)

filename = CACHE_PATHS['stopwords']
stopwords = retrieve_stopwords(filename)

graph = ProductGraph(hierarchy, stopwords)


# Custom streaming method
def stream(items):
    for item in items:
        yield f'{item}\n'


@app.route('/ingredients/hierarchy')
def hierarchy():
    products = graph.filter_products()
    return Response(stream(products), content_type='application/x-ndjson')


@app.route('/ingredients/query')
def query():
    descriptions = request.args.getlist('description[]')

    results = []
    match = None
    max_score = 0
    for doc_id, score in execute_queries(
        index=graph.index,
        queries=descriptions,
        stopwords=graph.stopwords,
        query_limit=-1
    ).items():
        product = graph.products_by_id[doc_id]
        if match is None or score > max_score:
            match = product
            max_score = score

    if match:
        parents = graph.find_parents(match)
        results.append({
            'product': match.name,
            'related': [parent.name for parent in parents],
        })

    return jsonify({'results': results})
