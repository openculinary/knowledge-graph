.PHONY: build deploy image lint tests

SERVICE=$(shell basename $(shell git rev-parse --show-toplevel))
REGISTRY=registry.openculinary.org
PROJECT=reciperadar

IMAGE_NAME=${REGISTRY}/${PROJECT}/${SERVICE}
IMAGE_COMMIT := $(shell git rev-parse --short HEAD)
IMAGE_TAG := $(strip $(if $(shell git status --porcelain --untracked-files=no), latest, ${IMAGE_COMMIT}))

build: image

deploy:
	kubectl apply -f k8s
	kubectl set image deployments -l app=${SERVICE} ${SERVICE}=${IMAGE_NAME}:${IMAGE_TAG}

image:
	$(eval container=$(shell buildah --storage-opt overlay.mount_program=/usr/bin/fuse-overlayfs from docker.io/library/python:3.8-alpine))
	buildah copy $(container) 'web' 'web'
	buildah copy $(container) 'requirements.txt'
	buildah run $(container) -- apk add py3-spacy --update-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing --
	buildah run $(container) -- adduser -h /srv/ -s /sbin/nologin -D -H gunicorn --
	buildah run $(container) -- chown gunicorn /srv/ --
	buildah run --user gunicorn $(container) -- pip install --no-warn-script-location --progress-bar off --requirement requirements.txt --user --
	# Begin: NOTE: Install spaCy language model
	buildah run --user gunicorn $(container) -- env PYTHONPATH=/usr/lib/python3.8/site-packages/ python -m spacy download en_core_web_sm --no-deps --
	# End: NOTE
	# Begin: HACK: For rootless compatibility across podman and k8s environments, unset file ownership and grant read+exec to binaries
	buildah run $(container) -- chown -R nobody:nobody /srv/ --
	buildah run $(container) -- chmod -R a+rx /srv/.local/bin/ --
	buildah run $(container) -- find /srv/ -type d -exec chmod a+rx {} \;
	# End: HACK
	buildah config --cmd '/srv/.local/bin/gunicorn web.app:app --bind :8000' --env PYTHONPATH=/usr/lib/python3.8/site-packages/ --port 8000 --user gunicorn $(container)
	buildah commit --quiet --rm --squash --storage-opt overlay.mount_program=/usr/bin/fuse-overlayfs $(container) ${IMAGE_NAME}:${IMAGE_TAG}

# Virtualenv Makefile pattern derived from https://github.com/bottlepy/bottle/
venv: venv/.installed requirements.txt requirements-dev.txt
	venv/bin/pip install --requirement requirements-dev.txt --quiet
	venv/bin/python -m spacy download en_core_web_sm --no-deps
	touch venv
venv/.installed:
	python3 -m venv venv
	venv/bin/pip install pip-tools
	touch venv/.installed

requirements.txt: requirements.in
	venv/bin/pip-compile --allow-unsafe --generate-hashes --no-header --quiet requirements.in

requirements-dev.txt: requirements.txt requirements-dev.in
	venv/bin/pip-compile --allow-unsafe --generate-hashes --no-header --quiet requirements-dev.in

lint: venv
	venv/bin/flake8 tests
	venv/bin/flake8 web

tests: venv
	venv/bin/pytest tests
