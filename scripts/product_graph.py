from scripts.search import (
    build_search_index,
    execute_queries,
)


class ProductGraph(object):

    def __init__(self, products):
        self.store_products(products)
        self.build_relationships()
        self.prune_relationships()
        self.calculate_depth()

    def store_products(self, products):
        self.products_by_id = {product.id: product for product in products}

    @property
    def index(self):
        if not hasattr(self, '_index'):
            self._index = build_search_index(
                self.products_by_id,
                lambda product: product.name
            )
        return self._index

    def find_children(self, product):
        results = execute_queries(self.index, [product.name])
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
