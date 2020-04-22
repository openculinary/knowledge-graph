from collections import defaultdict

from hashedindex import HashedIndex
from hashedindex.textparser import (
    word_tokenize,
    NullStemmer,
)


class NullAnalyzer():

    def process(self, input):
        for token in input.split(' '):
            for result in self.analyze_token(token):
                yield result

    def analyze_token(self, token):
        yield token


class SynonymAnalyzer(NullAnalyzer):

    def __init__(self, synonyms):
        self.synonyms = synonyms

    def analyze_token(self, token):
        token = self.synonyms.get(token) or token
        for token in token.split(' '):
            yield token


def tokenize(doc, stopwords=None, ngrams=None, stemmer=None, analyzer=None):
    stopwords = stopwords or []
    stemmer = stemmer or NullStemmer()
    analyzer = analyzer or NullAnalyzer()

    words = list(analyzer.process(doc))
    word_count = len(words)
    doc = ' '.join(words)

    ngrams = ngrams or word_count
    ngrams = min(ngrams, word_count, 4)
    ngrams = max(ngrams, 1)

    for ngrams in range(ngrams, 0, -1):
        for term in word_tokenize(doc, stopwords, ngrams, stemmer=stemmer):
            yield term


def add_to_search_index(index, doc_id, doc, stopwords=None, stemmer=None,
                        analyzer=None):
    stopwords = stopwords or []
    for term in tokenize(
            doc=doc,
            stopwords=stopwords,
            stemmer=stemmer,
            analyzer=analyzer):
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


def execute_queries(index, queries, stopwords=None, stemmer=None,
                    analyzer=None, query_limit=1):
    for query in queries:
        hits = execute_query(
            index=index,
            query=query,
            stopwords=stopwords,
            stemmer=stemmer,
            analyzer=analyzer,
            query_limit=query_limit
        )
        if hits:
            yield query, hits


def execute_query(index, query, stopwords=None, stemmer=None, analyzer=None,
                  query_limit=1):
    hits = defaultdict(lambda: 0)
    terms = defaultdict(lambda: [])
    query_count = 0
    for term in tokenize(query, stopwords=stopwords, stemmer=stemmer,
                         analyzer=analyzer):
        query_count += 1
        try:
            for doc_id in index.get_documents(term):
                doc_length = index.get_document_length(doc_id)
                hits[doc_id] += len(term) / doc_length
                terms[doc_id].append(term)
        except IndexError:
            pass
        if query_count == query_limit:
            break
    hits = [
        {'doc_id': doc_id, 'score': score, 'terms': terms[doc_id]}
        for doc_id, score in hits.items()
    ]
    return sorted(hits, key=lambda hit: hit['score'], reverse=True)


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]
