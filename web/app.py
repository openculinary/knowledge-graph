from flask import Flask, jsonify, request, Response

from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
    retrieve_stopwords,
)
from web.models.product_graph import ProductGraph
from web.search import (
    add_to_search_index,
    build_search_index,
    execute_queries,
)

app = Flask(__name__)

filename = CACHE_PATHS['hierarchy']
hierarchy = retrieve_hierarchy(filename)

filename = CACHE_PATHS['stopwords']
stopwords = retrieve_stopwords(filename)

graph = ProductGraph(hierarchy, stopwords)
stopwords = graph.filter_stopwords()


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

    candidates = []
    for doc_id in execute_queries(
        index=graph.index,
        queries=descriptions,
        stopwords=stopwords,
        query_limit=-1
    ):
        product = graph.products_by_id[doc_id]
        candidates.append(product.name)

    product_index = build_search_index()
    for doc_id, doc in enumerate(descriptions):
        add_to_search_index(product_index, doc_id, doc)

    match = None
    max_score = 0
    for candidate in candidates:
        for doc_id, score in execute_queries(
            index=product_index,
            queries=[candidate]
        ).items():
            if match is None or score > max_score:
                match = candidate
                max_score = score

    return jsonify({'results': [match] if match else []})
