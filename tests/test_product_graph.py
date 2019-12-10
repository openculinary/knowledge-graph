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
