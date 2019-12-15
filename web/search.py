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


def tokenize(doc, stopwords=None, ngrams=None):
    stopwords = stopwords or []
    stemmer = SnowballStemmer()

    word_count = len(doc.split(' '))
    ngrams = ngrams or word_count
    ngrams = min(word_count, 4)
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


def exact_match_exists(index, term):
    if term not in index:
        return False
    for doc_id in index.get_documents(term):
        frequency = index.get_term_frequency(term, doc_id)
        doc_length = index.get_document_length(doc_id)
        if frequency == doc_length:
            return True
    return False


def execute_queries(index, queries, stopwords=None, query_limit=1):
    results = {}
    for query in queries:
        hits = execute_query(index, query, stopwords, query_limit)
        results[query] = [{
            'doc_id': k,
            'score': v
        } for k, v in hits.items()]
    return results


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
    return hits


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]
