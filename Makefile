.PHONY: help install install-dev lint format test docs docs-serve build clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in editable mode
	pip install -e .

install-dev: ## Install with dev and pygame extras
	pip install -e .[dev,pygame]
	pre-commit install

install-docs: ## Install with docs extra
	pip install -e .[docs]

lint: ## Run ruff linter
	ruff check src/ example/ escape/

format: ## Auto-format code with ruff
	ruff format src/ example/ escape/
	ruff check --fix src/ example/ escape/

test: ## Run the test suite
	pytest -q

docs: ## Build Sphinx documentation
	sphinx-build -b html docs docs/_build/html

docs-serve: docs ## Build and open docs in a browser
	python -m webbrowser docs/_build/html/index.html

build: ## Build wheel and sdist
	python -m build

clean: ## Remove build artefacts
	rm -rf build/ dist/ docs/_build/ src/*.egg-info
