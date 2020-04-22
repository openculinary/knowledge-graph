from mock import patch

from string import punctuation

from web.models.product import Product


@patch('web.app.retrieve_hierarchy')
@patch('web.app.retrieve_stopwords')
def test_ingredient_query(stopwords, hierarchy, client):
    stopwords.return_value = []
    hierarchy.return_value = [
        Product(name='onion', frequency=10, parent_id=None),
        Product(name='baked bean', frequency=5, parent_id='bean'),
        Product(name='bean', frequency=20, parent_id=None),
        Product(name='tofu', frequency=20, parent_id=None),
        Product(name='firm tofu', frequency=10, parent_id='tofu'),
        Product(name='soft tofu', frequency=5, parent_id='tofu'),
    ]
    expected_products = {
        'large onion, diced': 'onion',
        'can of baked beans': 'baked beans',
        'block of firm tofu': 'firm tofu',
        'block tofu': 'tofu',
        'pressed soft tofu': 'soft tofu',
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_products.keys())}
    ).json['results']

    remove_punctuation = str.maketrans('', '', punctuation)
    for description, product in expected_products.items():
        basic_description = description.translate(remove_punctuation)
        markup = results[description]['markup']
        tagged_product = f'<mark>{product}</mark>'

        assert results[description]['product'] == product
        assert tagged_product in markup
        assert markup.replace(tagged_product, product) == basic_description
