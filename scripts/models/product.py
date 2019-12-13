import json

from scripts.search import tokenize


canonicalizations = {}
with open('scripts/data/canonicalizations.txt') as f:
    for line in f.readlines():
        if line.startswith('#'):
            continue
        source, target = line.strip().split(',')
        canonicalizations[source] = target


class Product(object):

    def __init__(self, name, frequency):
        self.name = self.canonicalize(name)
        self.frequency = frequency

        self.depth = None
        self.children = []
        self.parents = []
        self.primary_parent = None
        self.stopwords = []

    def __add__(self, other):
        self.frequency += other.frequency
        return self

    def __repr__(self):
        data = {
            'product': self.name,
            'recipe_count': self.frequency
        }

        tree_rendering = self.children or self.parents
        if tree_rendering:
            data.update({
                'id': self.id,
                'product': ' '.join(self.tokens),
            })

        if self.primary_parent:
            data.update({
                'parent_id': self.primary_parent.id
            })

        return '  ' * (self.depth or 0) + json.dumps(data, ensure_ascii=False)

    @property
    def id(self):
        return '_'.join(sorted(self.tokens))

    @staticmethod
    def canonicalize(name):
        words = name.split(' ')
        words = [canonicalizations.get(word) or word for word in words]
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

    def calculate_depth(self, path=None):
        if self.depth is not None:
            return self.depth

        path = path or []
        if self.id in path:
            self.depth = 0
            return -1
        path.append(self.id)

        depth = 0
        if self.primary_parent:
            depth = self.primary_parent.calculate_depth(path) + 1

        self.depth = depth
        return depth
