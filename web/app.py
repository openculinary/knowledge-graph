from flask import Flask

app = Flask(__name__)


import web.directions  # noqa
import web.ingredients  # noqa
import web.products  # noqa
