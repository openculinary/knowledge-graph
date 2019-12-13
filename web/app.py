from flask import Flask, Response

from web.loader import (
    CACHE_PATHS,
    retrieve_hierarchy,
)

app = Flask(__name__)


# Custom streaming method
def stream(items):
    for item in items:
        yield f'{item}\n'


@app.route('/ingredients/hierarchy')
def hierarchy():
    filename = CACHE_PATHS['hierarchy']
    hierarchy = retrieve_hierarchy(filename)
    return Response(stream(hierarchy), content_type='application/x-ndjson')
