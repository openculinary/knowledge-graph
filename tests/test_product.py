from web.models.product import Product


class MockGraph:
    def __init__(self, products):
        self.products = products
        self.products_by_id = {product.id: product for product in products}


def generate_product(name, id=None, frequency=1):
    return Product(id=id, name=name, frequency=frequency)


def test_merge_products():
    shared_id = "liquid_smoke"
    a1 = generate_product(id=shared_id, name="hickory liquid smoke")
    a2 = generate_product(id=shared_id, name="liquid smoke", frequency=10)

    a1 += a2

    assert a1.frequency == 11
    assert a1.name == "liquid smoke"

    assert a1.id == "liquid_smoke"
    assert a2.id == a1.id


def test_stopword_filtering():
    a1 = generate_product(name="chopped dried apricot")
    a1.stopwords = ["dri"]

    assert a1.to_doc() == "chop apricot"


def test_content_rendering():
    a1 = generate_product(name="chopped cooked chicken")
    a1.stopwords = ["chop", "cook"]

    assert a1.to_doc() == "chicken"


def test_metadata():
    a1 = generate_product(id="olive", name="olives")
    a2 = generate_product(id="black_olive", name="black olives")
    a3 = generate_product(id="green_olive", name="green olives")

    graph = MockGraph([a1, a2, a3])
    metadata = a3.get_metadata("green olive", graph)

    assert metadata["singular"] == "green olive"
    assert metadata["plural"] == "green olives"
    assert metadata["is_plural"] is False
