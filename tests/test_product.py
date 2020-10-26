import pytest

from web.models.product import Product


class MockGraph():

    def __init__(self, products):
        self.products = products
        self.products_by_id = {product.id: product for product in products}


def generate_product(name, parent=None, frequency=1):
    product = Product(name=name, frequency=frequency)
    if parent:
        product.parent_id = parent.id
    return product


def test_merge_products():
    a1 = generate_product(name='hickory liquid smoke', frequency=2)
    a2 = generate_product(name='liquid smoke', frequency=10)

    a1 += a2

    assert a1.frequency == 12
    assert a1.name == 'liquid smoke'

    assert a1.id == 'liquid_smoke'
    assert a2.id == a1.id


def test_calculate_depth():
    a1 = generate_product(name='a1')
    a2 = generate_product(name='a2', parent=a1)
    a3 = generate_product(name='a3', parent=a1)
    a4 = generate_product(name='a4', parent=a2)

    graph = MockGraph([a1, a2, a3, a4])
    [a.calculate_depth(graph) for a in graph.products]

    assert a1.depth == 0
    assert a2.depth == 1
    assert a3.depth == 1
    assert a4.depth == 2


def test_calculate_depth_avoids_loop():
    a1 = generate_product(name='a1')
    a2 = generate_product(name='a2', parent=a1)
    a3 = generate_product(name='a3', parent=a1)
    a4 = generate_product(name='a4', parent=a2)

    # Introduce a loop to the graph
    a1.parent_id = a4.id

    graph = MockGraph([a1, a2, a3, a4])
    [a.calculate_depth(graph) for a in graph.products]

    assert a1.depth == 2
    assert a2.depth == 0
    assert a3.depth == 3
    assert a4.depth == 1


def test_duplicate_consolidation():
    a1 = generate_product(name='sprig thyme')
    a2 = generate_product(name='thyme sprig')
    a3 = generate_product(name='fresh thyme sprig')
    a3.stopwords = ['fresh']

    assert a1.id == a2.id == a3.id


def test_stopword_filtering():
    a1 = generate_product(name='chopped dried apricot')
    a1.stopwords = ['dri']

    assert a1.to_doc() == 'chop apricot'


def test_content_rendering():
    a1 = generate_product(name='chopped cooked chicken')
    a1.stopwords = ['chop', 'cook']

    assert a1.to_doc() == 'chicken'


def test_metadata():
    a1 = generate_product(name='olives')
    a2 = generate_product(name='black olives', parent=a1)
    a3 = generate_product(name='greek black olives', parent=a2)

    graph = MockGraph([a1, a2, a3])
    metadata = a3.get_metadata('greek black olive', graph)

    assert metadata['singular'] == 'greek black olive'
    assert metadata['plural'] == 'greek black olives'
    assert metadata['is_plural'] is False
    assert 'olives' in metadata['ancestors']


def product_categories():
    return {
        'olive oil': 'oil_and_vinegar_and_condiments',
        'canola oil': 'oil_and_vinegar_and_condiments',
        'white wine vinegar': 'oil_and_vinegar_and_condiments',
        'ketchup': 'oil_and_vinegar_and_condiments',
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


def dietary_property_cases():
    return [
        ('beef', True, True, False, False),
        ('chicken', True, True, False, False),
        ('tofu', True, True, True, True),
        ('egg', False, True, False, True),
        ('tuna', True, True, False, False),
    ]


@pytest.mark.parametrize(
    "name,dairy_free,gluten_free,vegan,vegetarian",
    dietary_property_cases()
)
def test_product_dietary_properties(name, dairy_free, gluten_free, vegan,
                                    vegetarian):
    product = Product(name=name)

    assert product.is_dairy_free == dairy_free
    assert product.is_gluten_free == gluten_free
    assert product.is_vegan == vegan
    assert product.is_vegetarian == vegetarian


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


def test_product_id_transliteration():
    product = Product(name='jalapeño pepper')

    assert product.id == 'jalapeno_pepper'
