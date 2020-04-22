from mock import patch

from web.models.product import Product


@patch('web.app.retrieve_hierarchy')
@patch('web.app.retrieve_stopwords')
def test_ingredient_query(stopwords, hierarchy, client):
    stopwords.return_value = []
    hierarchy.return_value = [
        Product(name='onion', frequency=10, parent_id=None),
        Product(name='baked bean', frequency=5, parent_id='bean'),
        Product(name='bean', frequency=20, parent_id=None),
    ]
    expected_products = {
        'large onion, diced': 'onion',
        'can of baked beans': 'baked beans',
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_products.keys())}
    ).json['results']

    for description, product in expected_products.items():
        assert results[description]['product'] == product
        markup = results[description]['markup']
        tagged_product = f'<mark>{product}</mark>'
        assert tagged_product in markup
