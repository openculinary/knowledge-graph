from scripts.product import Product
from scripts.product_graph import ProductGraph


def test_tofu_hierarchy():
    tofu = Product(name='tofu')
    firm_tofu = Product(name='firm tofu')
    soft_tofu = Product(name='soft tofu')

    graph = ProductGraph(products=[firm_tofu, soft_tofu, tofu])

    assert len(graph.roots) == 1
    assert tofu in graph.roots
    assert firm_tofu.primary_parent == tofu
    assert soft_tofu.primary_parent == tofu
