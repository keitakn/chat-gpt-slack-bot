.PHONY: lint format ci

lint:
	flake8 .

format:
	black .

ci: lint
	poetry run black --check .
