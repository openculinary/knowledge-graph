from scripts.product import Product
from scripts.product_graph import ProductGraph


def generate_product(name):
    return Product(name=name, frequency=1)


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
