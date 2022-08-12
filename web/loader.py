import json
import os

import requests

from web.models.product import Product


CACHE_PATHS = {
    "stopwords": "web/data/generated/stopwords.txt",
    "appliance_queries": "web/data/equipment/appliances.txt",
    "utensil_queries": "web/data/equipment/utensils.txt",
    "vessel_queries": "web/data/equipment/vessels.txt",
}


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]


def retrieve_stopwords(filename):
    if not os.path.exists(filename):
        raise RuntimeError(f"Could not read stopwords from: {filename}")

    print(f"Reading stopwords from {filename}")
    with open(filename) as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue
            yield line.strip()


def retrieve_hierarchy():
    url = "http://backend-service/products/hierarchy"
    print(f"Reading hierarchy from {url}")

    text = requests.get(url).content.decode("utf-8")
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        product = json.loads(line)
        yield Product(
            id=product["id"],
            name=product["product"],
            frequency=product["recipe_count"],
            nutrition=product.get("nutrition"),
        )
