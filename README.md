# RecipeRadar Knowledge Graph

The RecipeRadar knowledge graph stores and provides access to recipe and ingredient relationship information.

This information includes facts such as 'lettuce is-a vegetable' as well as potential ingredient substitutions.

### Product Parsing

Ingredient descriptions generally include some combination of a quantity (i.e. `1 kg`) and a product (i.e. `potatoes`).  Since they are written as unstructured text in most recipes, parsing products can be a challenge.

The [`backend`](https://github.com/openculinary/backend/) service provides the source-of-truth for product metadata, and it makes this available at the [`/products/hierarchy`](https://github.com/openculinary/backend/blob/cd029da0bd9caab7f490f5299018934db10ed0ec/reciperadar/api/products.py#L51-L70) endpoint.

The knowledge graph loads this data at runtime, and we build an in-process search-engine index that allows us to find candidate ingredient matches, which are then narrowed down to a single best-match per ingredient line.

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](https://www.github.com/openculinary/infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```sh
$ make lint tests
```

## Local Deployment

To deploy the service to the local infrastructure environment, execute the following commands:

```sh
$ make
$ make deploy
```
