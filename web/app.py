from collections import defaultdict

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


@app.before_first_request
def preload_graph():
    filename = CACHE_PATHS['hierarchy']
    hierarchy = retrieve_hierarchy(filename)

    filename = CACHE_PATHS['stopwords']
    stopwords = retrieve_stopwords(filename)

    app.graph = ProductGraph(hierarchy, stopwords)
    app.products = app.graph.filter_products()
    app.stopwords = app.graph.filter_stopwords()


# Custom streaming method
def stream(items):
    for item in items:
        yield f'{item}\n'


@app.route('/ingredients/hierarchy')
def hierarchy():
    return Response(stream(app.products), content_type='application/x-ndjson')


@app.route('/ingredients/query', methods=['POST'])
def query():
    descriptions = request.form.getlist('descriptions[]')

    # Find all documents matching any of the requested descriptions
    results = execute_queries(
        index=app.graph.index,
        queries=descriptions,
        stopwords=app.stopwords,
        query_limit=-1
    )

    # For each description, retrieve products which matched the search
    candidates = set()
    for description, hits in results:
        for hit in hits:
            doc_id = hit['doc_id']
            product = app.graph.products_by_id[doc_id]
            candidates.add(product.name)

    # Build a local search index over the descriptions
    description_index = build_search_index()
    for doc_id, doc in enumerate(descriptions):
        add_to_search_index(description_index, doc_id, doc)

    # Query the list of candidate products within the description index
    results = execute_queries(
        index=description_index,
        queries=candidates
    )

    # Pick the best match for each description
    description_matches = {}
    description_scores = defaultdict(lambda: 0.0)
    for candidate, hits in results:
        for hit in hits:
            doc_id, score = hit['doc_id'], hit['score']
            if score > description_scores[doc_id]:
                description_matches[doc_id] = candidate
                description_scores[doc_id] = score
            break

    return jsonify({
        'results': {
            description: description_matches.get(i)
            for i, description in enumerate(descriptions)
        }
    })
