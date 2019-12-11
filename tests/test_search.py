from scripts.search import tokenize


def test_tokenize_stopwords():
    content = 'red bell peppers diced'
    stopwords = ['dice']

    tokens = tokenize(content, stopwords, ngrams=3)
    tokens = [token for token in tokens]

    assert tokens == [('red', 'bell', 'pepper')]
