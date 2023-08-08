SHELL := /bin/bash

.PHONY: all
all: requirements

.PHONY: clean
clean:
	rm -Rf dist django_redis_metrics.egg-info
	rm -rf dist

.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install --upgrade pip-tools
	pip-compile -rU --no-emit-index-url requirements.in
	pip-compile -rU --no-emit-index-url docs/requirements.in -o docs/requirements.txt

.PHONY: build
build:
	python -m build

.PHONY: upload
upload:
	python -m twine upload --repository pypi dist/*