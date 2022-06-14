from unittest.mock import patch

from web.app import app
from web.models.product import Product


@patch('web.ingredients.retrieve_hierarchy')
@patch('web.ingredients.retrieve_stopwords')
def test_ingredient_query(stopwords, hierarchy, client):
    # HACK: Ensure that app initialization methods (re)run during this test
    app._got_first_request = False

    stopwords.return_value = []
    hierarchy.return_value = [
        Product(id='onion', name='onion', frequency=10, parent_id=None),
        Product(id='baked_bean', name='baked bean', parent_id='bean'),
        Product(id='bean', name='bean', frequency=20, parent_id=None),
        Product(id='tofu', name='tofu', frequency=20, parent_id=None),
        Product(id='firm_tofu', name='firm tofu', parent_id='tofu'),
        Product(id='jalapeno', name='jalapeño', frequency=5),
        Product(id='soft_tofu', name='soft tofu', parent_id='tofu'),
        Product(id='soy_milk', name='soy milk', frequency=5, parent_id=None),
        Product(id='red_bell_pepper', name='red bell pepper', frequency=5),
    ]

    expected_results = {
        'large onion, diced': {
            'markup': 'large <mark>onion</mark>, diced',
            'product': 'onion',
            'product_id': 'onion',
        },
        'can of Baked Beans': {
            'markup': 'can of <mark>Baked Beans</mark>',
            'product': 'baked beans',
            'product_id': 'baked_bean',
        },
        'block of firm tofu': {
            'markup': 'block of <mark>firm tofu</mark>',
            'product': 'firm tofu',
            'product_id': 'firm_tofu',
        },
        'block tofu': {
            'markup': 'block <mark>tofu</mark>',
            'product': 'tofu',
            'product_id': 'tofu',
        },
        'pressed soft tofu': {
            'markup': 'pressed <mark>soft tofu</mark>',
            'product': 'soft tofu',
            'product_id': 'soft_tofu',
        },
        'soymilk': {
            'markup': '<mark>soy milk</mark>',
            'product': 'soy milk',
            'product_id': 'soy_milk',
        },
        '250ml of soymilk (roughly one cup)': {
            'markup': '250ml of <mark>soy milk</mark> (roughly one cup)',
            'product': 'soy milk',
            'product_id': 'soy_milk',
        },
        'Sliced red bell pepper, as filling': {
            'markup': 'Sliced <mark>red bell pepper</mark>, as filling',
            'product': 'red bell pepper',
            'product_id': 'red_bell_pepper',
        },
        'jalapeño pepper': {
            'markup': '<mark>jalapeño</mark> pepper',
            'product': 'jalapeño',
            'product_id': 'jalapeno',
        },
        'tofu (either soft tofu or silken tofu is best)': {
            'markup': '<mark>tofu</mark> (either soft tofu or silken tofu is best)',
            'product': 'tofu',
            'product_id': 'tofu',
        },
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_results.keys())}
    ).json['results']

    for query, expected in expected_results.items():
        assert results[query]['product']['id'] == expected['product_id']
        assert results[query]['product']['product'] == expected['product']
        assert results[query]['query']['markup'] == expected['markup']
