from web.models.product import Nutrition


def test_nutrition_dict():
    n = Nutrition(
        product='test',
        protein=1.0,
        fat=2.0,
        carbohydrates=3.0,
        energy=4.0,
        fibre=5.0,
    )

    assert 'product' in n.to_dict()
    assert 'product' not in n.to_dict(include_product=False)
