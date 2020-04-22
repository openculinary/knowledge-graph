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
    doc = 'red bell peppers diced'
    stopwords = ['dice']

    tokens = list(tokenize(
        doc=doc,
        stopwords=stopwords,
        stemmer=Product.stemmer
    ))

    assert tokens[0] == ('red', 'bell', 'pepper')


def test_token_stemming():
    doc = 'onions, finely chopped'
    stopwords = ['fine', 'chop']

    tokens = list(tokenize(
        doc=doc,
        stopwords=stopwords,
        stemmer=Product.stemmer
    ))

    assert tokens[0] == ('onion',)


def test_token_synonyms():
    doc = 'soymilk'
    synonyms = {'soymilk': 'soy milk'}

    analyzer = SynonymAnalyzer(synonyms=synonyms)
    tokens = list(tokenize(
        doc=doc,
        analyzer=analyzer
    ))

    assert tokens == [('soy', 'milk'), ('soy',), ('milk',)]


def test_stemming_consistency():
    # some words change more than once under repeated snowball stemming
    # i.e. mayonnaise -> mayonnais -> mayonnai
    product = Product(name='mayonnaise', frequency=1)
    doc = product.to_doc()

    index = build_search_index()
    add_to_search_index(index, 0, doc)
    hits = execute_queries(index, [doc])

    assert next(hits)


def test_analysis_consistency():
    product = Product(name='soymilk', frequency=1)
    synonyms = {'soymilk': 'soy milk'}
    analyzer = SynonymAnalyzer(synonyms=synonyms)

    index = build_search_index()
    add_to_search_index(index, 0, product.to_doc(), analyzer=analyzer)
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
