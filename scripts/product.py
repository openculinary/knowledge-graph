from hashedindex import textparser
from pymmh3 import hash_bytes
import snowballstemmer

stemmer = snowballstemmer.stemmer('english')

misspellings = {}
with open('scripts/data/misspellings.txt') as f:
    for line in f.readlines():
        if line.startswith('#'):
            continue
        spelling, correction = line.strip().split(',')
        misspellings[spelling] = correction


class Product(object):

    def __init__(self, name, frequency):
        self.name = self.spell_correct(name)
        self.frequency = frequency

        self.depth = None
        self.children = []
        self.parents = []
        self.primary_parent = None
        self.stopwords = []

    def __add__(self, other):
        self.frequency += other.frequency
        return self

    @staticmethod
    def spell_correct(name):
        words = name.split(' ')
        words = [misspellings.get(word) or word for word in words]
        return ' '.join(words)

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
