from mock import patch

from scripts.product import Product
from scripts.product_graph import ProductGraph


def generate_product(name):
    return Product(name=name, frequency=1)


def test_product_aggregation():
    onion = generate_product(name='onion')
    onions = generate_product(name='onions')

    graph = ProductGraph(products=[onion, onions])

    assert len(graph.roots) == 1
    assert graph.roots[0].frequency == 2


def test_tofu_hierarchy():
    tofu = generate_product(name='tofu')
    firm_tofu = generate_product(name='firm tofu')
    soft_tofu = generate_product(name='soft tofu')

    graph = ProductGraph(products=[firm_tofu, soft_tofu, tofu])

    assert len(graph.roots) == 1
    assert tofu in graph.roots
    assert firm_tofu.primary_parent == tofu
    assert soft_tofu.primary_parent == tofu


def test_bananas_common_root():
    banana = generate_product(name='banana')
    peeled_bananas = generate_product(name='peeled bananas')
    whole_banana = generate_product(name='whole banana')

    graph = ProductGraph(products=[banana, peeled_bananas, whole_banana])

    assert len(graph.roots) == 1


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

    graph = ProductGraph(products=all_products)

    assert len(graph.roots) == 1
    root = graph.roots[0]
    assert len([p for p in all_products if p.primary_parent == root]) == 2


@patch.object(ProductGraph, 'get_stopwords')
def test_red_bell_pepper_parent_assignment(stopwords):
    stopwords.return_value = [('dice',)]

    bell_pepper_diced = generate_product(name='bell pepper, diced')
    red_bell_pepper = generate_product(name='red bell pepper')
    red_bell_pepper_diced = generate_product(name='red bell pepper, diced')

    all_products = [
        bell_pepper_diced,
        red_bell_pepper,
        red_bell_pepper_diced,
    ]

    graph = ProductGraph(products=all_products)

    assert len(graph.roots) == 1
    assert bell_pepper_diced.stopwords == ['dice']
    assert red_bell_pepper_diced.stopwords == ['dice']

    # TODO: Find a more elegant pattern to handle reference updates
    red_bell_pepper = graph.products_by_id[red_bell_pepper.id]
    red_bell_pepper_diced = graph.products_by_id[red_bell_pepper_diced.id]

    assert red_bell_pepper.primary_parent == graph.roots[0]
    assert red_bell_pepper_diced.primary_parent == graph.roots[0]
