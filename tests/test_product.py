from scripts.product import Product


def generate_product(name, parent=None):
    product = Product(name=name, frequency=1)
    product.primary_parent = parent
    return product


def test_calculate_depth():
    a1 = generate_product(name='a1')
    a2 = generate_product(name='a2', parent=a1)
    a3 = generate_product(name='a3', parent=a1)
    a4 = generate_product(name='a4', parent=a2)

    [a.calculate_depth() for a in [a1, a2, a3, a4]]

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
    a1.primary_parent = a4

    [a.calculate_depth() for a in [a1, a2, a3, a4]]

    assert a1.depth == 2
    assert a2.depth == 0
    assert a3.depth == 3
    assert a4.depth == 1


def test_canonicalization():
    name_input = 'cod filet'
    name_expected = 'cod fillet'

    a1 = generate_product(name=name_input)

    assert a1.name == name_expected


def test_duplicate_consolidation():
    a1 = generate_product(name='sprig thyme')
    a2 = generate_product(name='thyme sprig')
    a3 = generate_product(name='fresh thyme sprig')
    a3.stopwords = ['fresh']

    assert a1.id == a2.id == a3.id


def test_stopword_token_filtering():
    a1 = generate_product(name='chopped dried apricot')
    a1.stopwords = ['dri']

    assert a1.tokens == ('chop', 'apricot')


def test_content_rendering():
    a1 = generate_product(name='chopped cooked chicken')
    a1.stopwords = ['chop', 'cook']

    assert a1.content == 'chicken'
