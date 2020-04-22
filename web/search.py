from collections import defaultdict

from hashedindex import HashedIndex
from hashedindex.textparser import word_tokenize
from snowballstemmer import stemmer


class SnowballStemmer():

    stemmer_en = stemmer('english')

    def stem(self, x):
        # TODO: Remove double-stemming
        # mayonnaise -> mayonnais -> mayonnai
        return self.stemmer_en.stemWord(self.stemmer_en.stemWord(x))


def tokenize(doc, stopwords=None, ngrams=None, stemmer=SnowballStemmer):
    stopwords = stopwords or []
    stemmer = stemmer() if stemmer else None

    word_count = len(doc.split(' '))
    ngrams = ngrams or word_count
    ngrams = min(ngrams, word_count, 4)
    ngrams = max(ngrams, 1)

    for ngrams in range(ngrams, 0, -1):
        for term in word_tokenize(doc, stopwords, ngrams, stemmer=stemmer):
            yield term


def add_to_search_index(index, doc_id, doc, stopwords=None):
    stopwords = stopwords or []
    for term in tokenize(doc, stopwords):
        index.add_term_occurrence(term, doc_id)


def build_search_index():
    return HashedIndex()


def execute_exact_query(index, term):
    if term not in index:
        return
    for doc_id in index.get_documents(term):
        frequency = index.get_term_frequency(term, doc_id)
        doc_length = index.get_document_length(doc_id)
        if frequency == doc_length:
            return doc_id


def execute_queries(index, queries, stopwords=None, query_limit=1):
    for query in queries:
        hits = execute_query(index, query, stopwords, query_limit)
        if hits:
            yield query, hits


def execute_query(index, query, stopwords=None, query_limit=1):
    hits = defaultdict(lambda: 0)
    query_count = 0
    for term in tokenize(query, stopwords):
        query_count += 1
        try:
            for doc_id in index.get_documents(term):
                doc_length = index.get_document_length(doc_id)
                hits[doc_id] += len(term) / doc_length
        except IndexError:
            pass
        if query_count == query_limit:
            break
    hits = [
        {'doc_id': doc_id, 'score': score}
        for doc_id, score in hits.items()
    ]
    return sorted(hits, key=lambda hit: hit['score'], reverse=True)


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]
