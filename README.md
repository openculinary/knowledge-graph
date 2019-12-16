# RecipeRadar Knowledge Graph

The RecipeRadar knowledge graph stores and provides access to recipe and ingredient relationship information.

This information includes facts such as 'lettuce is-a vegetable' as well as nutritional details about ingredients and potential ingredient substitutions.

### Product Parsing

Ingredient descriptions typically include some combination of a quantity (i.e. `1 kg`) and a product (i.e. `potatoes`).  Since they are typically written in free-text by recipe authors, parsing products can be a challenge.

The `scripts.products` module performs the following series of operations to load, refine and export a list of products which the `knowledge-graph` can use to identify best-matching products in free-text ingredient descriptions:

- Raw ingredient descriptions are loaded from file, and known-bad data is discarded
- Individual tokens within each description are canonicalized to reduce duplication
- Quantity-related tokens are discarded
- Descriptions are indexed and a list of stopwords is produced based on a [tf-idf](https://en.wikipedia.org/w/index.php?title=tf-idf) threshold.
- Stopwords are filtered to remove cases where exact-match products exist (i.e. 'olive')
- Per-document stopwords are identified
- Descriptions are re-indexed with the filtered stopword list applied
- For each product, 'child' documents are identified which contain the product's terms
- For each product, a 'parent' document is identified based on the best match found
- Simplified descriptions are exported, including details of their location in the product tree

Known issues:

- Document IDs are generated dynamically, which works but is 'fragile'
- Spelling corrections are important but currently handled via manual entry in 'canonicalizations.txt'
- It'd be useful to provide token [highlighting](https://www.elastic.co/guide/en/elasticsearch/reference/7.5/search-request-body.html#request-body-search-highlighting) in responses, particularly for cases where the plurality/stemming of the match differs from the input text
- Stopword metadata is not yet persisted or used effectively; they could, for example, be used to identify the collection of ways in which individual ingredients can be prepared ('diced', 'minced', ...)

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](https://www.github.com/openculinary/infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```
pipenv install --dev
pipenv run make
```

## Local Deployment

To deploy the service to the local infrastructure environment, execute the following commands:

```
sudo sh -x ./build.sh
sh -x ./deploy.sh
```

## Operations

To update the cached product list, calculate new stopwords, and regenerate the product hierarchy, use the following commands respectively:

```
pipenv run python -m scripts.products --update
pipenv run python -m scripts.stopwords --update
pipenv run python -m scripts.hierarchy --update
```
