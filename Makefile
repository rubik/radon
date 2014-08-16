.PHONY: tests cov htmlcov pep8 pylint docs dev-deps test-deps publish coveralls

tests:
	python radon/tests/run.py

cov:
	coverage erase && coverage run --include "radon/*" --omit "radon/__init__.py,radon/cli.py,radon/tests/*" radon/tests/run.py
	coverage report -m

htmlcov: cov
	coverage html

pep8:
	pep8 radon --exclude "radon/tests"

pylint:
	pylint --rcfile pylintrc radon

docs:
	cd docs && make html

test-deps:
	pip install -r test_requirements.pip

publish:
	python setup.py sdist bdist_wheel register upload
	python setup.py develop

coveralls: test-deps cov
	coveralls
