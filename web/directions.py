from collections import defaultdict
from functools import lru_cache
from flask import jsonify, request
from hashedixsearch import HashedIXSearch
from snowballstemmer import stemmer
# import spacy
# from spacy.symbols import VERB
from stop_words import get_stop_words as get_stopwords

from web.app import app
from web.loader import (
    CACHE_PATHS,
    load_queries,
)


class EquipmentStemmer:
    stemmer_en = stemmer("english")

    @lru_cache(maxsize=4096)
    def stem(self, x):
        return self.stemmer_en.stemWord(x)


stopwords = get_stopwords("en")
# nlp = spacy.load("en_core_web_sm")
appliance_queries = load_queries(CACHE_PATHS["appliance_queries"])
utensil_queries = load_queries(CACHE_PATHS["utensil_queries"])
vessel_queries = load_queries(CACHE_PATHS["vessel_queries"])


def matches_by_document(index, queries, stemmer):
    results_by_document = defaultdict(lambda: set())
    query_hits = index.query_batch(queries, stopwords=stopwords)
    for result, hits in query_hits:
        for hit in hits:
            results_by_document[hit["doc_id"]].add(result)
    return results_by_document


@app.route("/directions/query", methods=["POST"])
def equipment():
    descriptions = request.form.getlist("descriptions[]")

    stemmer = EquipmentStemmer()
    index = HashedIXSearch(stemmer=stemmer)
    for doc_id, doc in enumerate(descriptions):
        index.add(doc_id, doc, ngrams=2, stopwords=stopwords)

    query_matrix = {
        "equipment": {
            "appliance": appliance_queries,
            "utensil": utensil_queries,
            "vessel": vessel_queries,
        },
    }

    # Run the query matrix against the document set and collect entities by doc
    entities_by_doc = defaultdict(list)
    for entity_type in query_matrix:
        for entity_category in query_matrix[entity_type]:
            queries = query_matrix[entity_type][entity_category]
            queries_by_doc = matches_by_document(index, queries, stemmer)
            for doc_id, queries in queries_by_doc.items():
                for query in queries:
                    term = next(index.tokenize(query))
                    entities_by_doc[doc_id].append(
                        {
                            "name": query,
                            "term": term,
                            "type": entity_type,
                            "category": entity_category,
                        }
                    )

    # Collect unique verbs found in each input description
    for doc_id, description in enumerate(descriptions):
        tokens = []  # TODO: nlp(description)
        verbs = {token.text for token in tokens if token.pos == VERB}
        for verb in verbs:
            term = next(index.tokenize(verb))
            entities_by_doc[doc_id].append(
                {
                    "term": term,
                    "type": "verb",
                    "category": "action",
                }
            )

    # Collect all entities for each document and then generate doc markup
    markup_by_doc = {}
    for doc_id, entities in entities_by_doc.items():
        terms = []
        term_attributes = {}
        for entity in entities:
            term, entity_type, entity_category = (
                entity["term"],
                entity["type"],
                entity["category"],
            )
            terms.append(term)
            term_attributes[term] = {
                "class": f"{entity_type} {entity_category}",
            }
        markup_by_doc[doc_id] = index.highlight(
            doc=descriptions[doc_id],
            terms=terms,
            case_sensitive=False,
            term_attributes=term_attributes,
        )

    results = []
    for doc_id, description in enumerate(descriptions):
        results.append(
            {
                "index": doc_id,
                "description": description,
                "markup": markup_by_doc.get(doc_id),
                "entities": [
                    {
                        "name": entity["name"],
                        "type": entity["type"],
                        "category": entity["category"],
                    }
                    for entity in entities_by_doc.get(doc_id, [])
                    if entity.get("name") is not None
                ],
            }
        )
    return jsonify(results)
