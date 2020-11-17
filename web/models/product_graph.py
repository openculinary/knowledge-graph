from hashedixsearch import (
    add_to_search_index,
    build_search_index,
    execute_query_exact,
    tokenize,
)

from web.models.product import Product


class ProductGraph(object):

    def __init__(self, products, stopwords=None):
        stopwords = list(stopwords or [])
        self.products_by_id = {}
        self.product_index = self.build_index(products, stopwords)
        self.stopwords = list(self.process_stopwords(stopwords))
        self.stopword_index = self.build_stopword_index()

    def build_index(self, products, stopwords):
        index = build_search_index()

        clearwords = set(self.get_clearwords())
        product_stopwords = []
        for stopword in stopwords or []:
            if stopword not in clearwords:
                product_stopwords.append(stopword)

        count = 0
        for product in products:
            count += 1
            if count % 1000 == 0:
                print(f'- {count} documents indexed')

            product.stopwords = product_stopwords
            add_to_search_index(
                index=index,
                doc_id=product.id,
                doc=product.to_doc(),
                count=product.frequency,
            )
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
                for term in tokenize(line, stemmer=Product.stemmer):
                    if not term:
                        continue
                    yield term[0]

    def process_stopwords(self, stopwords):
        clearwords = list(self.get_clearwords())
        for stopword in stopwords:
            for term in tokenize(
                doc=stopword,
                stopwords=clearwords,
                stemmer=Product.stemmer
            ):
                if not term:
                    continue
                if execute_query_exact(self.product_index, term):
                    continue
                yield stopword

    def build_stopword_index(self):
        index = build_search_index()
        for doc_id, stopword in enumerate(self.stopwords):
            add_to_search_index(index, doc_id, stopword)
        return index

    def filter_products(self):
        for product in self.products_by_id.values():
            for term in tokenize(
                doc=product.name,
                ngrams=1,
                stemmer=Product.stemmer
            ):
                doc_id = execute_query_exact(self.stopword_index, term)
                if doc_id is not None:
                    product.stopwords.append(self.stopwords[doc_id])
            if tokenize(product.name, product.stopwords):
                yield product

    def filter_stopwords(self):
        return self.stopwords
