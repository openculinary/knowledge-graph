from functools import lru_cache
import json

from hashedixsearch import HashedIXSearch
import inflect
from snowballstemmer import stemmer
from unidecode import unidecode

from web.models.nutrition import Nutrition


class Product(object):
    class ProductStemmer:

        stemmer_en = stemmer("english")

        @lru_cache(maxsize=4096)
        def stem(self, x):
            x = unidecode(x)
            # TODO: Remove double-stemming
            # mayonnaise -> mayonnais -> mayonnai
            return self.stemmer_en.stemWord(self.stemmer_en.stemWord(x))

    stemmer = ProductStemmer()
    inflector = inflect.engine()

    def __init__(self, name, id=None, parent_id=None, frequency=0, nutrition=None):
        self.name = name
        self.id = id
        self.parent_id = parent_id
        self.frequency = max(frequency, 1)

        self.stopwords = []

        nutrition.pop("product", None) if nutrition else None
        self.nutrition = Nutrition(**nutrition) if nutrition else None

    def __add__(self, other):
        name = self.name if len(self.name) < len(other.name) else other.name
        self.name = name
        self.frequency += other.frequency
        return self

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self):
        data = {
            "id": self.id,
            "parent_id": self.parent_id,
            "product": self.name,
            "recipe_count": self.frequency,
        }
        if self.nutrition:
            data.update({"nutrition": self.nutrition.to_dict()})
        return data

    def tokenize(self, stopwords=True, stemmer=True, analyzer=True):
        for term in HashedIXSearch().tokenize(
            doc=self.name,
            stopwords=self.stopwords if stopwords else [],
            stemmer=self.stemmer if stemmer else None,
        ):
            for subterm in term:
                yield subterm
            if len(term) > 1:
                return

    def to_doc(self):
        tokens = self.tokenize()
        return " ".join(tokens)

    @lru_cache(maxsize=4096)
    def _static_metadata(self, graph):
        singular = Product.inflector.singular_noun(self.name)
        singular = singular or self.name
        plural = Product.inflector.plural_noun(singular)
        nutrition = self.nutrition.to_dict() if self.nutrition else None

        return {
            "id": self.id,
            "singular": singular,
            "plural": plural,
            "nutrition": nutrition,
        }

    def get_metadata(self, description, graph):
        metadata = self._static_metadata(graph)
        is_plural = metadata["plural"] in description.lower()
        metadata["is_plural"] = is_plural
        metadata["product"] = metadata["plural" if is_plural else "singular"]
        return metadata
