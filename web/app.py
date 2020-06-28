from flask import Flask

from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
    retrieve_stopwords,
)
from web.models.product_graph import ProductGraph

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


import web.ingredients
