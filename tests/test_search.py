from web.models.product import Product
from web.search import (
    build_search_index,
    add_to_search_index,
    exact_match_exists,
    execute_queries,
    tokenize,
)


def test_tokenize_stopwords():
    content = 'red bell peppers diced'
    stopwords = ['dice']

    tokens = list(tokenize(content, stopwords))

    assert tokens[0] == ('red', 'bell', 'pepper')


def test_token_stemming():
    content = 'onions, finely chopped'
    stopwords = ['fine', 'chop']

    tokens = list(tokenize(content, stopwords))

    assert tokens[0] == ('onion',)


def test_stemming_consistency():
    # some words change more than once under repeated snowball stemming
    # i.e. mayonnaise -> mayonnais -> mayonnai
    content = Product(name='mayonnaise', frequency=1)

    index = build_search_index()
    add_to_search_index(index, 0, content.content)
    hits = execute_queries(index, [content.name])

    assert hits


def test_exact_match():
    content = 'whole onion'
    stopwords = ['whole']

    index = build_search_index()
    add_to_search_index(index, 0, content, stopwords)

    term = ('onion',)
    assert exact_match_exists(index, term)


def test_exact_match_duplicate():
    content = 'whole onion'
    stopwords = ['whole']

    index = build_search_index()
    add_to_search_index(index, 0, content, stopwords)
    add_to_search_index(index, 0, content, stopwords)

    term = ('onion',)
    assert exact_match_exists(index, term)
