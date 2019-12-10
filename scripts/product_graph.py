from scripts.search import (
    build_search_index,
    execute_queries,
)


class ProductGraph(object):

    def __init__(self, products):
        self.store_products(products)
        self.build_index()

        stopwords = self.get_stopwords()
        self.tag_products(stopwords)

        products = self.products_by_id.values()
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

    def tag_products(self, stopwords):
        for stopword in stopwords:
            for product_id in self.index.get_documents(stopword):
                product = self.products_by_id[product_id]
                product.stopwords += stopword

    def exact_match_exists(self, term):
        for product_id in self.index.get_documents(term):
            product = self.products_by_id.get(product_id)
            if product.content == term[0]:
                return True
        return False

    def get_stopwords(self):
        stopwords = []
        if not hasattr(self, 'index'):
            return stopwords

        stopword_exceptions = ['red', 'white']
        for term in self.index.terms():
            if len(term) > 1:
                continue
            if term[0] in stopword_exceptions:
                continue
            tfidf = self.index.get_total_tfidf(term)
            if tfidf < 250:
                continue
            # TODO: Likely inefficient; stopwords have high doc counts
            if self.exact_match_exists(term):
                continue
            stopwords.append(term)
        return stopwords

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

                parent_tokens = parent.name.split(' ')
                primary_parent_tokens = primary_parent.name.split(' ')
                if len(parent_tokens) > len(primary_parent_tokens):
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
