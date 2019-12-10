from hashedindex import textparser
from pymmh3 import hash_bytes
import snowballstemmer

stemmer = snowballstemmer.stemmer('english')


class Product(object):

    def __init__(self, name, frequency):
        self.text = name
        self.name = self.canonicalize_name(name)
        self.frequency = frequency

        self.id = hash_bytes(self.name)
        self.depth = None
        self.children = []
        self.parents = []
        self.primary_parent = None

    def __add__(self, other):
        self.frequency += other.frequency
        return self

    @staticmethod
    def canonicalize_name(name):
        ngrams = len(name.split(' '))
        tokens = []
        for name_tokens in textparser.word_tokenize(name, ngrams=ngrams):
            tokens += list(name_tokens)
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
