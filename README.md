# RecipeRadar Python Template

This repository provides a template for building RecipeRadar web application services in Python.

A single endpoint and corresponding empty test are provided, along with dependencies to build and run the service.

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

### Note

You shouldn't really find yourself deploying or running the `python-template` service; you should instead copy the contents of this template to a new repository and replace all references to `python-template` with your service name.
