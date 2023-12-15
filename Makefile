.PHONY: format lint f tests cov htmlcov pep8 pylint docs dev-deps test-deps publish coveralls

source_dirs = radon
isort = isort -rc $(source_dirs)
black = black --line-length 79 --skip-string-normalization \
		--target-version py27 $(source_dirs)
flake8 = flake8 $(source_dirs)

format:
	$(isort)
	$(black)

lint:
	$(flake8)

f: format lint

tests: cov

cov:
	py.test --cov radon --cov-report term-missing --cov-report xml .

htmlcov: cov
	coverage html

pep8:
	pep8 radon --exclude "radon/tests" --ignore "E731"

pylint:
	pylint --rcfile pylintrc radon

docs:
	cd docs && make html

test-deps:
	pip install -r test_requirements.txt

publish:
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/*
	python setup.py develop

coveralls: test-deps cov
	coveralls
