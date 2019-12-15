import json

from web.search import tokenize


class Product(object):

    def __init__(self, name, frequency, parent_id=None):
        self.name = self.canonicalize(name)
        self.frequency = frequency
        self.parent_id = parent_id

        self.depth = None
        self.children = []
        self.parents = []
        self.stopwords = []

    def __add__(self, other):
        self.frequency += other.frequency
        return self

    def __repr__(self):
        data = self.to_dict(include_hierarchy=self.children or self.parents)
        return '  ' * (self.depth or 0) + json.dumps(data, ensure_ascii=False)

    def to_dict(self, include_hierarchy=False):
        data = {
            'product': self.canonicalize(self.name, self.stopwords),
            'recipe_count': self.frequency
        }
        if include_hierarchy:
            data.update({
                'id': self.id,
                'parent_id': self.parent_id,
                'depth': self.depth
            })
        return data

    @property
    def id(self):
        return '_'.join(sorted(self.tokens))

    @staticmethod
    def canonicalize(name, stopwords=None):
        words = name.split(' ')
        words = [word for word in words if list(tokenize(word, stopwords))]
        return ' '.join(words)

    @property
    def tokens(self):
        terms = tuple()
        for term in tokenize(self.name, self.stopwords):
            if len(term) > 1:
                return term
            terms += term
        return terms

    @property
    def content(self):
        return ' '.join(self.tokens)

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
