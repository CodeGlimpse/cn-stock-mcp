PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: setup setup-dev test test-all ci clean

setup:
	$(PIP) install --upgrade pip
	$(PIP) install -e .

setup-dev:
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]

test:
	pytest -q -m "not live"

test-all:
	pytest -q

ci:
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]
	pytest -q -m "not live"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov build dist *.egg-info
