from collections import defaultdict

from hashedindex import HashedIndex, textparser
from stop_words import get_stop_words

stopwords = get_stop_words('en')


def add_to_search_index(index, doc_id, doc):
    for ngrams in [1, 2]:
        for term in textparser.word_tokenize(doc, stopwords, ngrams):
            index.add_term_occurrence(term, doc_id)


def build_search_index(docs=None):
    index = HashedIndex()
    for doc_id, doc in enumerate(docs or []):
        add_to_search_index(index, doc_id, doc)
    return index


def build_query_terms(docs):
    for doc in docs:
        for ngrams in [2, 1]:
            for term in textparser.word_tokenize(doc, stopwords, ngrams):
                yield doc, term
                break
            else:
                continue
            break


def execute_queries(index, queries):
    hits = defaultdict(set)
    for query, term in build_query_terms(queries):
        try:
            for doc_id in index.get_documents(term):
                hits[doc_id].add(query)
        except IndexError:
            continue
    return hits


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]
