from flask import abort, jsonify

from web.app import app


@app.route('/products/<product_id>')
def product(product_id):
    product = app.graph.products_by_id.get(product_id)
    if not product:
        return abort(404)

    metadata = product.get_metadata(product.name, app.graph)

    return jsonify({
        'results': {
            product.name: {
                'product': metadata,
            }
        }
    })
