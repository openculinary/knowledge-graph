from web.search import (
    add_to_search_index,
    build_search_index,
    execute_exact_query,
    execute_query,
    tokenize,
)


class ProductGraph(object):

    def __init__(self, products, stopwords=None):
        self.products_by_id = {}
        self.index = self.build_index(products)
        self.stopwords = list(self.process_stopwords(stopwords))
        self.stopword_index = self.build_stopword_index()
        self.roots = []

    def generate_hierarchy(self):
        self.build_relationships()
        self.assign_parents()
        self.calculate_depth()
        return self.roots

    def build_index(self, products):
        index = build_search_index()

        count = 0
        for product in products:
            count += 1
            if count % 1000 == 0:
                print(f'- {count} documents indexed')

            add_to_search_index(index, product.id, product.content)
            if product.id not in self.products_by_id:
                self.products_by_id[product.id] = product
            else:
                self.products_by_id[product.id] += product
        print(f'- {count} documents indexed')
        return index

    def get_clearwords(self):
        with open('web/data/clear-words.txt') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                line = line.strip().lower()
                for term in tokenize(line):
                    yield term[0]

    def calculate_stopwords(self):
        for term in self.index.terms():
            if len(term) > 1:
                continue
            tfidf = self.index.get_total_tfidf(term)
            if tfidf < 45:
                continue
            yield term[0]

    def process_stopwords(self, stopwords):
        clearwords = list(self.get_clearwords())
        stopwords = stopwords or self.calculate_stopwords()
        for stopword in stopwords:
            for term in tokenize(stopword, clearwords):
                if execute_exact_query(self.index, term):
                    continue
                yield stopword

    def build_stopword_index(self):
        index = build_search_index()
        for doc_id, stopword in enumerate(self.stopwords):
            add_to_search_index(index, doc_id, stopword)
        return index

    def get_byproducts(self):
        with open('web/data/byproducts.txt') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                byproduct, parent = line.strip().lower().split(',')
                yield parent, byproduct

    def filter_products(self):
        for product in self.products_by_id.values():
            for term in tokenize(product.name, ngrams=1):
                doc_id = execute_exact_query(self.stopword_index, term)
                if doc_id is not None:
                    product.stopwords.append(self.stopwords[doc_id])
            if tokenize(product.name, product.stopwords):
                yield product

    def filter_stopwords(self):
        return self.stopwords

    def find_children(self, product):
        hits = execute_query(self.index, product.content)
        for hit in hits:
            doc_id = hit['doc_id']
            if doc_id != product.id:
                yield doc_id

    def find_parents(self, product):
        if product.parent_id:
            parent = self.products_by_id.get(product.parent_id)
            if not parent:
                return
            yield parent
            for parent in self.find_parents(parent):
                yield parent

    def build_relationships(self):

        # Assign byproducts to their parent ingredients
        for parent, byproduct in self.get_byproducts():

            # Find the parent product
            parent_hits = execute_query(self.index, parent)
            if not parent_hits:
                continue

            parent_id = parent_hits[0]['doc_id']
            parent = self.products_by_id.get(parent_id)
            parent.domain = 'byproducts'

            # Find all of the byproducts the parent relates to
            hits = execute_query(self.index, byproduct)
            for hit in hits:
                child_id = hit['doc_id']
                if child_id == parent_id:
                    continue
                child = self.products_by_id[child_id]
                child.domain = 'byproducts'
                child.parents.append(parent.id)
                parent.children.append(child.id)

        for parent in self.products_by_id.values():

            # Skip ingredients that have already been assigned children
            if parent.children:
                continue

            # Find ingredients that are named similarly to the parent element
            child_ids = self.find_children(parent)
            for child_id in child_ids:
                child = self.products_by_id[child_id]
                if child.domain is parent.domain:
                    child.parents.append(parent.id)
                    parent.children.append(child_id)

    def assign_parents(self):
        # Find a parent product for each product in the graph
        for product in self.products_by_id.values():

            # Find the parent with the most tokens
            primary_parent = None
            for parent_id in product.parents:
                parent = self.products_by_id[parent_id]
                if primary_parent is None:
                    primary_parent = parent
                if len(parent.tokens) > len(primary_parent.tokens):
                    primary_parent = parent

            # Assign the parent
            if primary_parent:
                product.parent_id = primary_parent.id

    def calculate_depth(self):
        for product in self.products_by_id.values():
            product.calculate_depth(self)
            if product.depth == 0:
                self.roots.append(product)
