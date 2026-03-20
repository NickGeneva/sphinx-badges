.PHONY: docs
docs:
	uv run sphinx-build -b html docs docs/_build/html

PORT ?= 8001
.PHONY: serve
serve:
	uv run python -m http.server $(PORT) --directory docs/_build/html
