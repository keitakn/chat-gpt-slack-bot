.PHONY: lint format

lint:
	flake8 .

format:
	black .
