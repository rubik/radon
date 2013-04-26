.PHONY: tests cov htmlcov pep8 pylint docs deps publish

tests:
	python radon/tests/run.py

cov:
	coverage erase && coverage run --include "radon/*" --omit "radon/__init__.py,radon/cli.py,radon/tests/*" radon/tests/run.py
	coverage report

htmlcov: cov
	coverage html

pep8:
	pep8 radon --exclude "tests"

pylint:
	pylint --rcfile pylintrc radon

docs:
	cd docs && make html

deps:
	pip install -r dev_requirements.pip

publish:
	python setup.py sdist bdist_wheel register upload
