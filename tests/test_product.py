import pytest

from web.models.product import Product


class MockGraph():

    def __init__(self, products):
        self.products = products
        self.products_by_id = {product.id: product for product in products}


def generate_product(name, id=None, parent=None, frequency=1):
    product = Product(id=id, name=name, frequency=frequency)
    if parent:
        product.parent_id = parent.id
    return product


def test_merge_products():
    shared_id = 'liquid_smoke'
    a1 = generate_product(id=shared_id, name='hickory liquid smoke')
    a2 = generate_product(id=shared_id, name='liquid smoke', frequency=10)

    a1 += a2

    assert a1.frequency == 11
    assert a1.name == 'liquid smoke'

    assert a1.id == 'liquid_smoke'
    assert a2.id == a1.id


def test_stopword_filtering():
    a1 = generate_product(name='chopped dried apricot')
    a1.stopwords = ['dri']

    assert a1.to_doc() == 'chop apricot'


def test_content_rendering():
    a1 = generate_product(name='chopped cooked chicken')
    a1.stopwords = ['chop', 'cook']

    assert a1.to_doc() == 'chicken'


def test_metadata():
    a1 = generate_product(id='olive', name='olives')
    a2 = generate_product(id='black_olive', name='black olives', parent=a1)
    a3 = generate_product(id='green_olive', name='green olives', parent=a2)

    graph = MockGraph([a1, a2, a3])
    metadata = a3.get_metadata('green olive', graph)

    assert metadata['singular'] == 'green olive'
    assert metadata['plural'] == 'green olives'
    assert metadata['is_plural'] is False
    assert 'olives' in metadata['ancestors']


def product_categories():
    return {
        'olive oil': 'oil_and_vinegar_and_condiments',
        'canola oil': 'oil_and_vinegar_and_condiments',
        'white wine vinegar': 'oil_and_vinegar_and_condiments',
        'ketchup': 'oil_and_vinegar_and_condiments',
        'chicken': 'meat_and_deli',
    }


def test_chicken_contents():
    product = generate_product(name='chicken')

    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_breast_contents():
    product = generate_product(name='chicken breast')

    assert 'chicken breast' in product.contents
    assert 'chicken' in product.contents
    assert 'meat' in product.contents


def test_chicken_exclusion_contents():
    exclusions = ['broth', 'bouillon', 'soup']

    for exclusion in exclusions:
        product = generate_product(name=f'chicken {exclusion}')

        assert f'chicken {exclusion}' in product.contents
        assert 'chicken' not in product.contents

        # TODO: identify meat-derived products
        # assert 'meat' in contents


def test_contents_singularization():
    product = generate_product(name='mushrooms')

    assert 'mushroom' in product.contents
    assert 'mushrooms' not in product.contents


@pytest.mark.parametrize('name,category', product_categories().items())
def test_product_categories(name, category):
    product = generate_product(name=name)

    assert product.category == category


def product_property_cases():
    return [
        ('beef', True, True, False, False, False),
        ('chicken', True, True, False, False, False),
        ('tofu', True, True, True, True, False),
        ('egg', False, True, False, True, True),
        ('tuna', True, True, False, False, False),
        ('salt', True, True, True, True, True),
    ]


@pytest.mark.parametrize(
    "name,dairy_free,gluten_free,vegan,vegetarian,kitchen_staple",
    product_property_cases()
)
def test_product_properties(name, dairy_free, gluten_free, vegan,
                            vegetarian, kitchen_staple):
    product = Product(name=name)

    assert product.is_dairy_free == dairy_free
    assert product.is_gluten_free == gluten_free
    assert product.is_vegan == vegan
    assert product.is_vegetarian == vegetarian
    assert product.is_kitchen_staple == kitchen_staple


def canonicalization_cases():
    return {
        'cod filet': 'cod fillet',
        'black beans': 'black bean',
        'coriander': 'cilantro',
    }.items()


@pytest.mark.parametrize('name,expected', canonicalization_cases())
def test_product_canonicalization(name, expected):
    product = Product(name=name)

    assert product.to_doc() == expected
