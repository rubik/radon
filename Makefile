.PHONY: tests cov htmlcov pep8 pylint docs dev-deps test-deps publish coveralls

tests:
	python tests/run.py

cov:
	coverage erase && coverage run --include "radon/*" --omit "radon/__init__.py,radon/cli.py,radon/tests/*" tests/run.py
	coverage report -m

htmlcov: cov
	coverage html

pep8:
	pep8 radon

pylint:
	pylint --rcfile pylintrc radon

docs:
	cd docs && make html

dev-deps:
	pip install -r dev_requirements.pip

test-deps:
	pip install -r test_requirements.pip

publish:
	python setup.py sdist bdist_wheel register upload

coveralls: test-deps cov
	coveralls
