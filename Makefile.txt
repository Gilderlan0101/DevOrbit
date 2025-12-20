.PHONY: lint
lint:
	ruff check --fix
	ruff format

