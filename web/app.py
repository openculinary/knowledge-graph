from collections import defaultdict

from flask import Flask, jsonify, request

from web.loader import (
    CACHE_PATHS,
    canonicalize,
    retrieve_hierarchy,
    retrieve_stopwords,
)
from web.models.product_graph import ProductGraph
from web.search import (
    add_to_search_index,
    build_search_index,
    execute_queries,
    execute_query,
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


def find_product_candidates(descriptions):
    results = execute_queries(
        index=app.graph.index,
        queries=descriptions,
        stopwords=app.stopwords,
        query_limit=-1
    )
    for description, hits in results:
        for hit in hits:
            product = app.graph.products_by_id[hit['doc_id']]
            yield product


@app.route('/ingredients/query', methods=['POST'])
def query():
    # Retrieve and canonicalize the query input descriptions
    descriptions = request.form.getlist('descriptions[]')
    canonicalizations = [
        canonicalize(description) for description in descriptions
    ]

    # Build a local search index over the canonicalized descriptions
    description_index = build_search_index()
    for doc_id, doc in enumerate(canonicalizations):
        add_to_search_index(description_index, doc_id, doc)

    # Track the best match for each canonicalized description
    products = defaultdict(lambda: None)
    scores = defaultdict(lambda: 0.0)
    for candidate in find_product_candidates(canonicalizations):
        hits = execute_query(
            index=description_index,
            query=candidate.name
        )
        for hit in hits:
            doc_id, score, terms = hit['doc_id'], hit['score'], hit['terms']
            if score > scores[doc_id]:
                products[doc_id] = candidate, terms
                scores[doc_id] = score

    # Build per-product result metadata
    metadata = defaultdict(lambda: None)
    for doc_id, (product, terms) in products.items():
        description = descriptions[doc_id]
        metadata[doc_id] = product.get_metadata(description, app.graph, terms)

    return jsonify({
        'results': {
            description: metadata[doc_id]
            for doc_id, description in enumerate(descriptions)
        }
    })
