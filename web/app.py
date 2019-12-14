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

    # Find all documents matching any of the requested descriptions
    results = execute_queries(
        index=graph.index,
        queries=descriptions,
        stopwords=stopwords,
        query_limit=-1
    )

    # For each description, retrieve products which matched the search
    candidates = {}
    for description, hits in results.items():
        candidates[description] = [
            graph.products_by_id[hit['doc_id']]
            for hit in hits
        ]

    # Flatten a list of the candidate product names
    candidates = [
        candidate.name for candidates
        in candidates.values() for candidate in candidates
    ]

    # Build a local search index over the descriptions
    description_index = build_search_index()
    for doc_id, doc in enumerate(descriptions):
        add_to_search_index(description_index, doc_id, doc)

    # Query the list of candidate products within the description index
    results = execute_queries(
        index=description_index,
        queries=candidates
    )

    # Find the best matches for each description
    description_matches = defaultdict(lambda: {'match': None, 'score': 0})
    for candidate, hits in results.items():
        for hit in hits:
            doc_id, score = hit['doc_id'], hit['score']
            if score > description_matches[doc_id]['score']:
                description_matches[doc_id] = {
                    'match': candidate,
                    'score': score,
                }

    return jsonify({
        'results': {
            description: description_matches[i]['match']
            for i, description in enumerate(descriptions)
        }
    })
