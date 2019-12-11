from scripts.search import (
    build_search_index,
    execute_queries,
)


class ProductGraph(object):

    def __init__(self, products):
        self.store_products(products)
        self.build_index()

        stopwords = self.get_stopwords()
        products = self.filter_products(stopwords)

        self.store_products(products)
        self.build_index()

        self.build_relationships()
        self.prune_relationships()
        self.calculate_depth()

    def store_products(self, products):
        self.products_by_id = {}
        for product in products:
            if product.id not in self.products_by_id:
                self.products_by_id[product.id] = product
            else:
                self.products_by_id[product.id] += product

    def build_index(self):
        self.index = build_search_index(
            self.products_by_id,
            lambda product: product.content,
        )

    def filter_products(self, stopwords):
        for stopword in stopwords:
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
            if tfidf < 50:
                continue
            # TODO: Likely inefficient; stopwords have high doc counts
            if self.exact_match_exists(term):
                continue
            yield term

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

    def prune_relationships(self):
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
