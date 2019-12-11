from collections import defaultdict

from hashedindex import HashedIndex, textparser
from snowballstemmer import stemmer

stemmer_en = stemmer('english')


def tokenize(doc, stopwords, ngrams):
    words = doc.split(' ')
    words = stemmer_en.stemWords(words)
    doc = ' '.join(words)
    for term in textparser.word_tokenize(doc, stopwords, ngrams):
        yield term


def add_to_search_index(index, doc_id, doc, stopwords):
    for ngrams in [1, 2, 3]:
        for term in tokenize(doc, stopwords, ngrams):
            index.add_term_occurrence(term, doc_id)


def build_search_index(docs_by_id, selector):
    index = HashedIndex()
    for doc_id, doc in docs_by_id.items():
        doc_content = selector(doc)
        add_to_search_index(index, doc_id, doc_content, [])
    return index


def build_query_terms(docs):
    for doc in docs:
        ngrams = len(doc.split(' '))
        for term in tokenize(doc, [], ngrams):
            yield doc, term


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
