from collections import defaultdict
from flask import jsonify, request
from hashedixsearch import (
    add_to_search_index,
    build_search_index,
    execute_queries,
    execute_query,
    highlight,
)

from web.app import app
from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
    retrieve_stopwords,
)
from web.models.product import Product
from web.models.product_graph import ProductGraph


@app.before_first_request
def preload_ingredient_data():
    filename = CACHE_PATHS['hierarchy']
    hierarchy = retrieve_hierarchy(filename)

    filename = CACHE_PATHS['stopwords']
    stopwords = retrieve_stopwords(filename)

    app.graph = ProductGraph(hierarchy, stopwords)
    app.products = app.graph.filter_products()
    app.stopwords = app.graph.filter_stopwords()


def find_product_candidates(products):
    queries = [product.name for product in products]
    results = execute_queries(
        index=app.graph.product_index,
        queries=queries,
        stopwords=app.stopwords,
        stemmer=Product.stemmer,
        synonyms=Product.canonicalizations,
        query_limit=-1
    )
    for description, hits in results:
        for hit in hits:
            product = app.graph.products_by_id[hit['doc_id']]
            yield product


@app.route('/ingredients/query', methods=['POST'])
def ingredients():
    descriptions = request.form.getlist('descriptions[]')
    products = [Product(name=description) for description in descriptions]

    # Build a local search index over the product descriptions
    description_index = build_search_index()
    for doc_id, product in enumerate(products):
        add_to_search_index(
            index=description_index,
            doc_id=doc_id,
            doc=product.name,
            stemmer=product.stemmer,
            synonyms=Product.canonicalizations,
        )

    # Track the best match for each product
    results = defaultdict(lambda: None)
    scores = defaultdict(lambda: 0.0)
    for candidate in find_product_candidates(products):
        hits = execute_query(
            index=description_index,
            query=candidate.name,
            stemmer=candidate.stemmer,
            synonyms=Product.canonicalizations,
        )
        for hit in hits:
            doc_id, score, terms = hit['doc_id'], hit['score'], hit['terms']
            if score > scores[doc_id]:
                results[doc_id] = candidate, terms
                scores[doc_id] = score

    # Build per-query result metadata
    markup = defaultdict(lambda: None)
    metadata = defaultdict(lambda: None)
    for doc_id, (product, terms) in results.items():
        description = descriptions[doc_id]
        markup[doc_id] = highlight(
            query=description,
            terms=terms,
            stemmer=product.stemmer,
            synonyms=Product.canonicalizations,
            case_sensitive=False,
        )
        metadata[doc_id] = product.get_metadata(description, app.graph, terms)

    return jsonify({
        'results': {
            description: {
                'product': metadata[doc_id],
                'query': {
                    'markup': markup[doc_id],
                }
            }
            for doc_id, description in enumerate(descriptions)
        }
    })
