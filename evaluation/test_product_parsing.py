import pytest

import json
import requests


def training_data():
    with open('evaluation/data/product-parsing.txt') as f:
        for line in f.readlines():
            recipe_id, cases = line.strip().split(' ', 1)
            cases = json.loads(cases)
            yield recipe_id, cases


@pytest.mark.parametrize('recipe_id, cases', training_data())
def test_training_data(recipe_id, cases, client):
    descriptions = [key for key in cases.keys()]
    results = client.get(
        '/ingredients/query',
        query_string={'description[]': descriptions}
    ).json['results']

    matches, exact_matches, misses = 0, 0, {}
    for description, product in cases.items():
        result = results.get(description)
        if result and result in product:
            exact_matches += result == product
            matches += 1
            continue
        misses[description] = {
            'expected': product,
            'actual': result
        }

    score = float(matches) / len(cases)
    assert score >= 0.75, misses


def evaluation_data():
    recipes = requests.get('http://localhost/api/recipes/sample?limit=100')
    for recipe in recipes.json():
        cases = {
            ingredient['description']: ingredient['product']['product']
            for ingredient in recipe['ingredients']
        }
        yield recipe['id'], cases


@pytest.mark.parametrize('recipe_id, cases', evaluation_data())
def test_evaluation_data(recipe_id, cases, client):
    descriptions = [key for key in cases.keys()]
    results = client.get(
        '/ingredients/query',
        query_string={'description[]': descriptions}
    ).json['results']

    matches, exact_matches, misses = 0, 0, {}
    for description, product in cases.items():
        result = results.get(description)
        if result and result in product:
            exact_matches += result == product
            matches += 1
            continue
        misses[description] = {
            'expected': product,
            'actual': result
        }

    score = float(matches) / len(cases)
    assert score >= 0.75, misses
