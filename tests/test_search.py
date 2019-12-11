from scripts.search import tokenize


def test_tokenize_stopwords():
    content = 'red bell peppers diced'
    stopwords = ['dice']

    tokens = tokenize(content, stopwords)
    tokens = [token for token in tokens]

    assert tokens[0] == ('red', 'bell', 'pepper')
