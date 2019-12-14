import pytest

import json


def product_query_evaluations():
    with open('evaluation/data/product-parsing.txt') as f:
        for line in f.readlines():
            recipe_id, cases = line.strip().split(' ', 1)
            cases = json.loads(cases)
            yield recipe_id, cases


@pytest.mark.parametrize('recipe_id, cases', product_query_evaluations())
def test_query_evaluation(recipe_id, cases, client):
    matches, exact_matches, misses = 0, 0, {}
    for description, product in cases.items():
        results = client.get(
            '/ingredients/query',
            query_string={'description[]': [description]}
        ).json['results']

        result = results[0] if results else None
        if result == product:
            exact_matches += 1
        if result and result in product:
            matches += 1
            continue

        misses[description] = {
            'expected': product,
            'actual': result
        }

    score = float(matches) / len(cases)
    assert score > 0.75, misses
