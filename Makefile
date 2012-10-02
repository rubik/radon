.PHONY: tests cov htmlcov

tests:
	python radon/tests/run.py

cov:
	coverage erase && coverage run --include "radon/*" --omit "radon/__init__.py,radon/cli.py,radon/tests/*" radon/tests/run.py 

htmlcov: cov
	coverage html
