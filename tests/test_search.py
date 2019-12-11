from scripts.search import tokenize


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
