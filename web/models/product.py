import inflect
import json

from snowballstemmer import stemmer

from web.search import (
    tokenize,
    SynonymAnalyzer,
)


class Product(object):

    class ProductStemmer:

        stemmer_en = stemmer('english')

        def stem(self, x):
            # TODO: Remove double-stemming
            # mayonnaise -> mayonnais -> mayonnai
            return self.stemmer_en.stemWord(self.stemmer_en.stemWord(x))

    class ProductAnalyzer(SynonymAnalyzer):

        def __init__(self):
            canonicalizations = {}
            with open('web/data/canonicalizations.txt') as f:
                for line in f.readlines():
                    if line.startswith('#'):
                        continue
                    source, target = line.strip().split(',')
                    canonicalizations[source] = target
            super().__init__(canonicalizations)

    stemmer = ProductStemmer()
    analyzer = ProductAnalyzer()
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
            analyzer=self.analyzer if analyzer else None
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

    def get_markup(self, description, terms):

        # Apply markup to the input description text
        markup = ''
        for term in terms:

            # Generate unstemmed ngrams of the same length as the product match
            remaining_tokens = []
            n = len(term)
            tag = 0
            for tokens in tokenize(
                doc=description,
                ngrams=n,
                stemmer=None,
                analyzer=self.analyzer
            ):
                # If generated tokens are depleted, consume remaining tokens
                if len(tokens) < n and len(remaining_tokens) > 0:
                    tokens = remaining_tokens

                # Continue token-by-token advancement, closing any open tags
                tag -= 1
                if tag == 0:
                    markup += '</mark>'

                # If tokens are depleted and a tag is open, close after the tag
                if len(tokens) < n and tag > 0:
                    markup += f' {" ".join(tokens[:tag])}'
                    markup += '</mark>'
                    tokens = tokens[tag:]

                # If tokens are depleted, write remaining tokens to the output
                if len(tokens) < n:
                    markup += f' {" ".join(tokens)}'
                    break

                markup += ' '

                # Stem the original text to allow match equality comparsion
                text = ' '.join(tokens)
                for stemmed_tokens in tokenize(
                    doc=text,
                    ngrams=n,
                    stemmer=self.stemmer,
                    analyzer=self.analyzer
                ):
                    break

                # Open a tag marker when we find a matching term
                if stemmed_tokens == term:
                    markup += f'<mark>'
                    tag = n

                # Append the next consumed original token when we do not
                markup += f'{tokens[0]}'
                remaining_tokens = tokens[1:]

        return markup.strip()

    def get_metadata(self, description, graph, terms=None):
        singular = Product.inflector.singular_noun(self.name)
        singular = singular or self.name
        plural = Product.inflector.plural_noun(singular)
        is_plural = plural in description
        markup = self.get_markup(description, terms or [])

        return {
            'markup': markup or None,
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
