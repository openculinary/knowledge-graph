from collections import defaultdict
from datetime import datetime, timedelta
from flask import jsonify, request
from hashedixsearch import HashedIXSearch

from web.app import app
from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
    retrieve_stopwords,
)
from web.models.product import Product
from web.models.product_graph import ProductGraph


@app.before_request
def preload_ingredient_data():
    # HACK: Only perform ingredient preloading for the ingredient query URL path
    if request.path != "/ingredients/query":
        return

    # Return cached product graph if it is available and has not yet expired
    if hasattr(app, "graph"):
        if datetime.utcnow() < app.graph_loaded_at + timedelta(hours=1):
            return

    # Otherwise, attempt to update the product graph
    hierarchy = retrieve_hierarchy()

    filename = CACHE_PATHS["stopwords"]
    stopwords = retrieve_stopwords(filename)

    app.graph = ProductGraph(hierarchy, stopwords)
    app.graph_loaded_at = datetime.utcnow()


def find_product_candidates(products):
    queries = [product.name for product in products]
    results = app.graph.product_index.query_batch(
        queries, stopwords=app.graph.stopwords, query_limit=-1
    )
    for description, hits in results:
        for hit in hits:
            product = app.graph.products_by_id[hit["doc_id"]]
            yield product


@app.route("/ingredients/query", methods=["POST"])
def ingredients():
    descriptions = request.form.getlist("descriptions[]")
    products = [Product(name=description) for description in descriptions]

    # Build a local search index over the product descriptions
    description_index = HashedIXSearch(stemmer=Product.stemmer)
    for doc_id, product in enumerate(products):
        description_index.add(doc_id, product.name)

    # Track the best match for each product
    results = defaultdict(lambda: None)
    scores = defaultdict(lambda: 0.0)
    for candidate in find_product_candidates(products):
        hits = description_index.query(candidate.name)
        for hit in hits:
            doc_id, score, terms = hit["doc_id"], hit["score"], hit["terms"]
            if score > scores[doc_id]:
                results[doc_id] = candidate, terms
                scores[doc_id] = score

    # Build per-query result metadata
    markup = defaultdict(lambda: None)
    metadata = defaultdict(lambda: None)
    for doc_id, (product, terms) in results.items():
        description = descriptions[doc_id]
        markup[doc_id] = description_index.highlight(
            doc=description, terms=terms, case_sensitive=False, limit=1
        )
        metadata[doc_id] = product.get_metadata(description, app.graph)

    return jsonify(
        {
            "results": {
                description: {
                    "product": metadata[doc_id],
                    "query": {
                        "markup": markup[doc_id],
                    },
                }
                for doc_id, description in enumerate(descriptions)
            }
        }
    )
