from web.search import (
    add_to_search_index,
    build_search_index,
    exact_match_exists,
    execute_query,
)


class ProductGraph(object):

    def __init__(self, products, stopwords=None):
        self.products_by_id = {}
        self.stopwords = list(stopwords or [])
        self.index = self.build_index(products)
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

    def filter_products(self):
        for term in self.get_stopterms():
            if term not in self.index:
                continue
            for product_id in self.index.get_documents(term):
                product = self.products_by_id[product_id]
                product.stopwords += term
        for product in self.products_by_id.values():
            if product.tokens:
                yield product

    def get_clearwords(self):
        clearwords = []
        with open('web/data/clear-words.txt') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                line = line.strip().lower()
                if not line:
                    continue
                clearwords.append(line)
        return clearwords

    def get_stopwords(self):
        if self.stopwords:
            for stopword in self.stopwords:
                yield stopword
            return
        for term in self.index.terms():
            if len(term) > 1:
                continue
            tfidf = self.index.get_total_tfidf(term)
            if tfidf < 50:
                continue
            yield term[0]

    def get_stopterms(self):
        clearwords = self.get_clearwords()
        for stopword in self.get_stopwords():
            if stopword in clearwords:
                continue
            term = tuple([stopword])
            if exact_match_exists(self.index, term):
                continue
            yield term

    def filter_stopwords(self):
        for term in self.get_stopterms():
            yield term[0]

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
        for parent in self.products_by_id.values():
            child_ids = self.find_children(parent)
            for child_id in child_ids:
                parent.children.append(child_id)
                self.products_by_id[child_id].parents.append(parent.id)

    def assign_parents(self):
        for product in self.products_by_id.values():
            primary_parent = None
            for parent_id in product.parents:
                parent = self.products_by_id[parent_id]
                if primary_parent is None:
                    primary_parent = parent
                if len(parent.tokens) > len(primary_parent.tokens):
                    primary_parent = parent
            if primary_parent:
                product.parent_id = primary_parent.id

    def calculate_depth(self):
        for product in self.products_by_id.values():
            product.calculate_depth(self)
            if product.depth == 0:
                self.roots.append(product)
