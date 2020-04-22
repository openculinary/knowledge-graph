from web.models.product import Product
from web.search import (
    build_search_index,
    add_to_search_index,
    execute_exact_query,
    execute_queries,
    tokenize,
    SynonymAnalyzer,
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


def test_token_synonyms():
    content = 'soymilk'
    synonyms = {'soymilk': 'soy milk'}

    analyzer = SynonymAnalyzer(synonyms=synonyms)
    tokens = list(tokenize(content, analyzer=analyzer))

    assert tokens == [('soy', 'milk'), ('soy',), ('milk',)]


def test_stemming_consistency():
    # some words change more than once under repeated snowball stemming
    # i.e. mayonnaise -> mayonnais -> mayonnai
    content = Product(name='mayonnaise', frequency=1)

    index = build_search_index()
    add_to_search_index(index, 0, content.content)
    hits = execute_queries(index, [content.name])

    assert next(hits)


def test_analysis_consistency():
    content = Product(name='soymilk', frequency=1)
    synonyms = {'soymilk': 'soy milk'}
    analyzer = SynonymAnalyzer(synonyms=synonyms)

    index = build_search_index()
    add_to_search_index(index, 0, content.content, analyzer=analyzer)
    hits = execute_queries(index, ['soy milk'], analyzer=analyzer)

    assert next(hits)


def test_exact_match():
    content = 'whole onion'
    stopwords = ['whole']

    index = build_search_index()
    add_to_search_index(index, 0, content, stopwords)

    term = ('onion',)
    assert execute_exact_query(index, term) == 0


def test_exact_match_duplicate():
    content = 'whole onion'
    stopwords = ['whole']

    index = build_search_index()
    add_to_search_index(index, 0, content, stopwords)
    add_to_search_index(index, 0, content, stopwords)

    term = ('onion',)
    assert execute_exact_query(index, term) == 0
