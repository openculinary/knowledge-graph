from mock import patch

from web.models.product import Product


@patch('web.app.retrieve_hierarchy')
@patch('web.app.retrieve_stopwords')
def test_ingredient_query(stopwords, hierarchy, client):
    stopwords.return_value = []
    hierarchy.return_value = [
        Product(name='onion', frequency=10, parent_id=None),
    ]
    expected_products = {
        'large onion, diced, ': 'onion',
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_products.keys())}
    ).json['results']

    for description, product in expected_products.items():
        assert results[description]['product'] == product
        assert f'<mark>{product}</mark>' in results[description]['markup']
