from scripts.search import (
    build_search_index,
    execute_queries,
)


class ProductGraph(object):

    def __init__(self, products):
        self.products = products
        self.build_relationships()
        self.prune_relationships()
        self.calculate_depth()

    @property
    def products_by_id(self):
        if not hasattr(self, '_products_by_id'):
            self._products_by_id = {
                doc['id']: {
                    'id': doc['id'],
                    'product': doc['product'],
                    'children': [],
                    'parents': [],
                } for doc in self.products
            }
        return self._products_by_id

    @property
    def index(self):
        if not hasattr(self, '_index'):
            self._index = build_search_index(
                self.products_by_id,
                lambda doc: doc['product']
            )
        return self._index

    def find_children(self, product_id):
        product = self.products_by_id[product_id]['product']
        results = execute_queries(self.index, [product])
        children = set(results.keys())
        if product_id in children:
            children.remove(product_id)
        return children

    def build_relationships(self):
        for parent_id, parent in self.products_by_id.items():
            child_ids = self.find_children(parent_id)
            for child_id in child_ids:
                parent['children'].append(child_id)
                self.products_by_id[child_id]['parents'].append(parent_id)

    def prune_relationships(self):
        for product in self.products_by_id.values():
            primary_parent = None
            for parent_id in product['parents']:
                parent = self.products_by_id[parent_id]
                if primary_parent is None:
                    primary_parent = parent
                if len(parent['product'].split(' ')) > len(primary_parent['product'].split(' ')):
                    primary_parent = parent
            product['primary_parent'] = primary_parent

    def calculate_product_depth(self, product, path=None):
        if 'depth' in product:
            return product['depth']

        path = path or []
        if product['id'] in path:
            product['depth'] = 0
            return 0
        path.append(product['id'])

        depth = 0
        if product['primary_parent']:
            depth = self.calculate_product_depth(product['primary_parent'], path) + 1
        return depth

    def calculate_depth(self):
        for product in self.products_by_id.values():
            product['depth'] = self.calculate_product_depth(product)
