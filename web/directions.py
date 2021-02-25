from collections import defaultdict
from functools import lru_cache
import en_core_web_sm
from flask import jsonify, request
from hashedixsearch import HashedIXSearch
from snowballstemmer import stemmer
from spacy.symbols import VERB
from stop_words import get_stop_words as get_stopwords

from web.app import app
from web.loader import (
    CACHE_PATHS,
    load_queries,
)


class EquipmentStemmer:

    stemmer_en = stemmer('english')

    @lru_cache(maxsize=4096)
    def stem(self, x):
        return self.stemmer_en.stemWord(x)


stopwords = get_stopwords('en')


@app.before_first_request
def preload_equipment_data():
    app.nlp = en_core_web_sm.load()
    app.appliance_queries = load_queries(CACHE_PATHS['appliance_queries'])
    app.utensil_queries = load_queries(CACHE_PATHS['utensil_queries'])
    app.vessel_queries = load_queries(CACHE_PATHS['vessel_queries'])


def matches_by_document(index, queries, stemmer):
    results_by_document = defaultdict(lambda: set())
    query_hits = index.query_batch(queries, stopwords=stopwords)
    for result, hits in query_hits:
        for hit in hits:
            results_by_document[hit['doc_id']].add(result)
    return results_by_document


@app.route('/directions/query', methods=['POST'])
def equipment():
    descriptions = request.form.getlist('descriptions[]')

    stemmer = EquipmentStemmer()
    index = HashedIXSearch(stemmer=stemmer)
    for doc_id, doc in enumerate(descriptions):
        index.add(doc_id, doc, ngrams=2, stopwords=stopwords)

    query_matrix = {
        'equipment': {
            'appliance': app.appliance_queries,
            'utensil': app.utensil_queries,
            'vessel': app.vessel_queries,
        },
    }

    # Run the query matrix against the document set and collect entities by doc
    entities_by_doc = defaultdict(list)
    for entity_type in query_matrix:
        for entity_class in query_matrix[entity_type]:
            queries = query_matrix[entity_type][entity_class]
            queries_by_doc = matches_by_document(index, queries, stemmer)
            for doc_id, queries in queries_by_doc.items():
                for query in queries:
                    term = next(index.tokenize(query))
                    entities_by_doc[doc_id].append({
                        'name': query,
                        'term': term,
                        'attr': {'class': f'{entity_type} {entity_class}'},
                    })

    # Collect unique verbs found in each input description
    for doc_id, description in enumerate(descriptions):
        tokens = app.nlp(description)
        verbs = {token.text for token in tokens if token.pos == VERB}
        for verb in verbs:
            term = next(index.tokenize(verb))
            entities_by_doc[doc_id].append({
                'term': term,
                'attr': {'class': 'action'}
            })

    # Collect all entities for each document and then generate doc markup
    markup_by_doc = {}
    for doc_id, entities in entities_by_doc.items():
        terms = []
        term_attributes = {}
        for entity in entities:
            term, attr = entity['term'], entity['attr']
            terms.append(term)
            term_attributes[term] = attr
        markup_by_doc[doc_id] = index.highlight(
            doc=descriptions[doc_id],
            terms=terms,
            case_sensitive=False,
            term_attributes=term_attributes
        )

    results = []
    for doc_id, description in enumerate(descriptions):
        results.append({
            'index': doc_id,
            'description': description,
            'markup': markup_by_doc.get(doc_id),
            'entities': [
                {'name': entity['name']}
                for entity in entities_by_doc.get(doc_id, [])
                if entity.get('name') is not None
            ],
        })
    return jsonify(results)
