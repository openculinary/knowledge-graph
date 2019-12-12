from collections import defaultdict

from hashedindex import HashedIndex
from hashedindex.textparser import word_tokenize
from snowballstemmer import stemmer


class SnowballStemmer():

    stemmer_en = stemmer('english')

    def stem(self, x):
        return self.stemmer_en.stemWord(x)


def tokenize(doc, stopwords=None):
    stopwords = stopwords or []
    stemmer = SnowballStemmer()

    word_count = len(doc.split(' '))
    for ngrams in range(word_count, 0, -1):
        for term in word_tokenize(doc, stopwords, ngrams, stemmer=stemmer):
            yield term


def add_to_search_index(index, doc_id, doc, stopwords):
    for term in tokenize(doc, stopwords):
        index.add_term_occurrence(term, doc_id)


def build_search_index(docs_by_id, selector):
    index = HashedIndex()
    for doc_id, doc in docs_by_id.items():
        doc_content = selector(doc)
        add_to_search_index(index, doc_id, doc_content, [])
    return index


def build_query_terms(docs):
    for doc in docs:
        for term in tokenize(doc):
            yield doc, term


def execute_queries(index, queries):
    hits = defaultdict(set)
    for query, term in build_query_terms(queries):
        try:
            for doc_id in index.get_documents(term):
                hits[doc_id].add(query)
        except IndexError:
            pass
        break
    return hits


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]
