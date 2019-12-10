from hashedindex import textparser
from pymmh3 import hash_bytes
import snowballstemmer

stemmer = snowballstemmer.stemmer('english')


class Product(object):

    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency

        self.depth = None
        self.children = []
        self.parents = []
        self.primary_parent = None
        self.stopwords = []

    def __add__(self, other):
        self.frequency += other.frequency
        return self

    @property
    def id(self):
        return hash_bytes(self.content)

    @property
    def content(self):
        ngrams = len(self.name.split(' '))
        tokens = []
        for t in textparser.word_tokenize(self.name, self.stopwords, ngrams):
            tokens += t
        tokens = stemmer.stemWords(tokens)
        return ' '.join(tokens)

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
