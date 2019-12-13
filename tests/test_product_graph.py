from scripts.models.product import Product
from scripts.models.product_graph import ProductGraph


def generate_product(name):
    return Product(name=name, frequency=1)


def generate_hierarchy(products, stopwords=None):
    graph = ProductGraph(products, stopwords)
    return graph.generate_hierarchy()


def test_product_aggregation():
    onion = generate_product(name='onion')
    onions = generate_product(name='onions')

    roots = generate_hierarchy(products=[onion, onions])

    assert len(roots) == 1
    assert roots[0].frequency == 2


def test_tofu_hierarchy():
    tofu = generate_product(name='tofu')
    firm_tofu = generate_product(name='firm tofu')
    soft_tofu = generate_product(name='soft tofu')

    roots = generate_hierarchy(products=[firm_tofu, soft_tofu, tofu])

    assert len(roots) == 1
    assert tofu in roots
    assert firm_tofu.primary_parent == tofu
    assert soft_tofu.primary_parent == tofu


def test_bananas_common_root():
    banana = generate_product(name='banana')
    peeled_bananas = generate_product(name='peeled bananas')
    whole_banana = generate_product(name='whole banana')

    roots = generate_hierarchy(products=[banana, peeled_bananas, whole_banana])

    assert len(roots) == 1


def test_bell_pepper_categorization():
    bell_pepper = generate_product(name='bell pepper')
    red_bell_peppers = generate_product(name='red bell peppers')
    red_bell_pepper_diced = generate_product(name='red bell pepper, diced')
    green_bell_pepper = generate_product(name='green bell peppers')
    green_bell_pepper_halved = generate_product(name='half green bell pepper')

    all_products = [
        bell_pepper,
        red_bell_peppers,
        red_bell_pepper_diced,
        green_bell_pepper,
        green_bell_pepper_halved,
    ]

    roots = generate_hierarchy(products=all_products)

    assert len(roots) == 1
    assert len([p for p in all_products if p.primary_parent == roots[0]]) == 2


def test_red_bell_pepper_parent_assignment():
    bell_pepper_diced = generate_product(name='bell pepper, diced')
    red_bell_pepper = generate_product(name='red bell pepper')
    red_bell_pepper_diced = generate_product(name='red bell pepper, diced')

    all_products = [
        bell_pepper_diced,
        red_bell_pepper,
        red_bell_pepper_diced,
    ]

    graph = ProductGraph(products=all_products, stopwords=['dice'])
    products = graph.filter_products()

    graph = ProductGraph(products=products, stopwords=['dice'])
    roots = graph.generate_hierarchy()

    # TODO: Find a more elegant pattern to handle reference updates
    red_bell_pepper = graph.products_by_id[red_bell_pepper.id]
    red_bell_pepper_diced = graph.products_by_id[red_bell_pepper_diced.id]

    assert len(roots) == 1
    assert red_bell_pepper.primary_parent == roots[0]
    assert red_bell_pepper_diced.primary_parent == roots[0]
