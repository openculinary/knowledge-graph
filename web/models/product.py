from hashedixsearch import (
    tokenize,
)

import inflect
import json

from snowballstemmer import stemmer
from unidecode import unidecode


class Product(object):

    class ProductStemmer:

        stemmer_en = stemmer('english')

        def stem(self, x):
            x = unidecode(x)
            # TODO: Remove double-stemming
            # mayonnaise -> mayonnais -> mayonnai
            return self.stemmer_en.stemWord(self.stemmer_en.stemWord(x))

    stemmer = ProductStemmer()
    canonicalizations = {}
    inflector = inflect.engine()

    def __init__(self, name, frequency=0, parent_id=None):
        self.name = name
        self.frequency = frequency
        self.parent_id = parent_id

        self.depth = None
        self.children = []
        self.parents = []
        self.stopwords = []
        self.domain = None

        # TODO: Find a better place to perform this initialization
        if self.canonicalizations:
            return
        with open('web/data/canonicalizations.txt') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                source, target = line.strip().split(',')
                self.canonicalizations[source] = target

    def __add__(self, other):
        name = self.name if len(self.name) < len(other.name) else other.name
        self.name = name
        self.frequency += other.frequency
        return self

    def __repr__(self):
        data = self.to_dict(include_hierarchy=self.children or self.parents)
        return '  ' * (self.depth or 0) + json.dumps(data, ensure_ascii=False)

    def to_dict(self, include_hierarchy=False):
        data = {
            'product': self.name,
            'recipe_count': self.frequency
        }
        if include_hierarchy:
            data.update({
                'id': self.id,
                'domain': self.domain,
                'parent_id': self.parent_id,
                'depth': self.depth
            })
        return data

    def tokenize(self, stopwords=True, stemmer=True, analyzer=True):
        for term in tokenize(
            doc=self.name,
            stopwords=self.stopwords if stopwords else [],
            stemmer=self.stemmer if stemmer else None,
            synonyms=self.canonicalizations,
        ):
            for subterm in term:
                yield subterm
            if len(term) > 1:
                return

    @property
    def id(self):
        tokens = self.tokenize()
        return '_'.join(sorted(tokens))

    def to_doc(self):
        tokens = self.tokenize()
        return ' '.join(tokens)

    def calculate_depth(self, graph, path=None):
        if self.depth is not None:
            return self.depth

        path = path or []
        if self.id in path:
            self.depth = 0
            return -1
        path.append(self.id)

        depth = 0
        if self.parent_id:
            parent = graph.products_by_id[self.parent_id]
            depth = parent.calculate_depth(graph, path) + 1

        self.depth = depth
        return depth

    def get_metadata(self, description, graph, terms=None):
        singular = Product.inflector.singular_noun(self.name)
        singular = singular or self.name
        plural = Product.inflector.plural_noun(singular)
        is_plural = plural in description.lower()

        return {
            'id': self.id,
            'product': plural if is_plural else singular,
            'is_plural': is_plural,
            'singular': singular,
            'plural': plural,
            'category': self.category,
            'contents': self.contents,
            'ancestors': [ancestor.name for ancestor in self.ancestry(graph)],
        }

    def ancestry(self, graph):
        if not self.parent_id:
            return
        parent = graph.products_by_id.get(self.parent_id)
        if parent:
            yield parent
            for ancestor in parent.ancestry(graph):
                yield ancestor

    @property
    def category(self):
        content_categories = {
            'egg': 'dairy',
            'milk': 'dairy',

            'banana': 'fruit_and_veg',
            'berry': 'fruit_and_veg',
            'berries': 'fruit_and_veg',
            'garlic': 'fruit_and_veg',
            'onion': 'fruit_and_veg',
            'tomato': 'fruit_and_veg',

            'meat': 'meat_and_deli',

            'ketchup': 'oil_and_vinegar_and_condiments',
            'oil': 'oil_and_vinegar_and_condiments',
            'soy sauce': 'oil_and_vinegar_and_condiments',
            'vinegar': 'oil_and_vinegar_and_condiments',
        }
        categories = {
            'bakery',
            'dairy',
            'dry_goods',
            'fruit_and_veg',
            'meat_and_deli',
            'oil_and_vinegar_and_condiments',
        }
        for content in self.contents:
            if content in categories:
                return content
        for content in content_categories:
            if content in self.name.split(' '):
                if content_categories[content] in categories:
                    return content_categories[content]

    @property
    def contents(self):
        content_graph = {
            'baguette': 'bread',
            'bread': 'bread',
            'loaf': 'bread',

            'butter': 'dairy',
            'cheese': 'dairy',
            'milk': 'dairy',
            'yoghurt': 'dairy',
            'yogurt': 'dairy',

            'bacon': 'meat',
            'beef': 'meat',
            'chicken': 'meat',
            'ham': 'meat',
            'lamb': 'meat',
            'pork': 'meat',
            'sausage': 'meat',
            'steak': 'meat',
            'turkey': 'meat',
            'venison': 'meat',
        }
        exclusion_graph = {
            'meat': ['stock', 'broth', 'tomato', 'bouillon', 'soup', 'eggs'],
            'bread': ['crumbs'],
            'fruit_and_veg': ['green tomato'],
        }

        contents = {Product.inflector.singular_noun(self.name) or self.name}
        for content in content_graph:
            if content in self.name.split():
                excluded = False
                fields = [content, content_graph[content]]
                for field in fields:
                    for excluded_term in exclusion_graph.get(field, []):
                        excluded = excluded or excluded_term in self.name
                if excluded:
                    continue
                for field in fields:
                    singular = Product.inflector.singular_noun(field) or field
                    contents.add(singular)
        return list(contents)
