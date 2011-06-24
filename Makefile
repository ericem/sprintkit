.PHONY: clean test docs build

all: clean test

test:
	python setup.py nosetests

release:
	python setup.py release sdist upload

build:
	python setup.py build sdist

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

docs:
	$(MAKE) -C docs html
	$(MAKE) -C docs html dirhtml latex
	$(MAKE) -C docs/_build/latex all-pdf

