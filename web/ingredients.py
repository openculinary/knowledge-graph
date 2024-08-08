from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
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
        if datetime.now(tz=UTC) < app.graph_loaded_at + timedelta(hours=1):
            return

    # Otherwise, attempt to update the product graph
    hierarchy = retrieve_hierarchy()

    filename = CACHE_PATHS["stopwords"]
    stopwords = retrieve_stopwords(filename)

    app.graph = ProductGraph(hierarchy, stopwords)
    app.graph_loaded_at = datetime.now(tz=UTC)


def find_product_candidates(descriptions):
    results = app.graph.product_index.query_batch(
        descriptions, stopwords=app.graph.stopwords, query_limit=-1
    )
    for description, hits in results:
        for hit in hits:
            product = app.graph.products_by_id[hit["doc_id"]]
            yield product


@app.route("/ingredients/query", methods=["POST"])
def ingredients():
    descriptions = request.form.getlist("descriptions[]")

    # Filter-out content between parentheses
    unadorned_descriptions = []
    for description in descriptions:
        parens, unadorned_description = Counter(), ""
        for char in description:
            if char in {"(", "[", "{"}:
                parens[char] += 1
            if char in {")", "]", "}"}:
                parens[char] -= 1
            if not parens.total():
                unadorned_description += char
        unadorned_descriptions.append(unadorned_description)

    # Build a local search index over the product descriptions
    description_index = HashedIXSearch(stemmer=Product.stemmer)
    for doc_id, description in enumerate(unadorned_descriptions):
        description_index.add(doc_id, description)

    # Track the best match for each product
    results = defaultdict(lambda: None)
    scores = defaultdict(lambda: 0.0)
    for candidate in find_product_candidates(descriptions):
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
