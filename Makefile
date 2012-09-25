.PHONY: tests cov htmlcov

tests:
	python tests/run.py

cov:
	coverage erase && coverage run --include "radon/*" --omit "radon/__init__.py,radon/cli.py" tests/run.py 

htmlcov: cov
	coverage html
