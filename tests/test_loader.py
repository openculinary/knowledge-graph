import pytest

from scripts.loader import discard


def construct_product(product, recipe_count=10):
    return {'product': product, 'recipe_count': recipe_count}


def discard_cases():
    return {
        '__': True,
        '1kg beef': True,
        'céy': False,
        'tomato': False,
    }.items()


@pytest.mark.parametrize('product,expected', discard_cases())
def test_discard(product, expected):
    product = construct_product(product)

    result = discard(product)

    assert result is expected
