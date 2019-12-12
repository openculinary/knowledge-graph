from scripts.search import (
    add_to_search_index,
    build_search_index,
    execute_queries,
)


class ProductGraph(object):

    def __init__(self, products, stopwords=None):
        self.products_by_id = {}
        self.stopwords = stopwords or []
        self.index = self.build_index(products)

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
            if product.id not in self.products_by_id:
                self.products_by_id[product.id] = product
            else:
                self.products_by_id[product.id] += product
            add_to_search_index(index, product.id, product.content)
            if count % 1000 == 0:
                print(f'- {count} documents indexed')
        print(f'- {count} documents indexed')
        return index

    def filter_products(self):
        for stopword in self.stopwords:
            stopword = tuple([stopword])
            for product_id in self.index.get_documents(stopword):
                product = self.products_by_id[product_id]
                product.stopwords += stopword
        return [
            product for product in self.products_by_id.values()
            if product.tokens
        ]

    def exact_match_exists(self, term):
        for product_id in self.index.get_documents(term):
            product = self.products_by_id.get(product_id)
            if product.content == term[0]:
                return True
        return False

    def get_clearwords(self):
        clearwords = []
        with open('scripts/data/clear-words.txt') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                clearwords.append(line.strip().lower())
        return clearwords

    def get_stopwords(self):
        clearwords = self.get_clearwords()
        for term in self.index.terms():
            if len(term) > 1:
                continue
            if term[0] in clearwords:
                continue
            tfidf = self.index.get_total_tfidf(term)
            if tfidf < 250:
                continue
            # TODO: Likely inefficient; stopwords have high doc counts
            if self.exact_match_exists(term):
                continue
            yield term[0]

    def find_children(self, product):
        results = execute_queries(self.index, [product.content])
        children = set(results.keys())
        if product.id in children:
            children.remove(product.id)
        return children

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
            product.primary_parent = primary_parent

    def calculate_depth(self):
        for product in self.products_by_id.values():
            product.calculate_depth()

    @property
    def roots(self):
        return [
            product for product in self.products_by_id.values()
            if product.depth == 0
        ]
