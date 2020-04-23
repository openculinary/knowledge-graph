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
        Product(name='soy milk', frequency=5, parent_id=None),
        Product(name='red bell pepper', frequency=5, parent_id=None),
    ]
    expected_products = {
        'large onion, diced': 'onion',
        'can of baked beans': 'bake_bean',
        'block of firm tofu': 'firm_tofu',
        'block tofu': 'tofu',
        'pressed soft tofu': 'soft_tofu',
        'soymilk': 'milk_soy',
        'quart of soymilk in a cup': 'milk_soy',
        'sliced red bell pepper as filling': 'bell_pepper_red',
    }
    products = {
        'onion': 'onion',
        'bake_bean': 'baked beans',
        'firm_tofu': 'firm tofu',
        'tofu': 'tofu',
        'soft_tofu': 'soft tofu',
        'milk_soy': 'soy milk',
        'bell_pepper_red': 'red bell pepper',
    }

    results = client.post(
        '/ingredients/query',
        data={'descriptions[]': list(expected_products.keys())}
    ).json['results']

    remove_punctuation = str.maketrans('', '', punctuation)
    for description, product_id in expected_products.items():
        basic_description = ' '.join(Product.analyzer.process(description))
        basic_description = basic_description.translate(remove_punctuation)

        product = products[product_id]
        markup = results[description]['query']['markup']
        tagged_product = f'<mark id="{product_id}">{product}</mark>'

        assert results[description]['product']['id'] == product_id
        assert results[description]['product']['product'] == product
        assert tagged_product in markup
        assert markup.replace(tagged_product, product) == basic_description
