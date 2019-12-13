# RecipeRadar Knowledge Graph

The RecipeRadar knowledge graph stores and provides access to recipe and ingredient relationship information.

This information includes facts such as 'lettuce is-a vegetable' as well as nutritional details about ingredients and potential ingredient substitutions.

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
