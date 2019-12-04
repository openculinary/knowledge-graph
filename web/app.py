from flask import Flask, abort, jsonify, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def root():
    products = request.args.getlist('products[]')
    if not products:
        return abort(400)

    return jsonify(products)
