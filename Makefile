.PHONY: build
build: venv
	@python -m build

.PHONY: lint
lint: venv
	@ruff check .

.PHONY: venv
venv:
	@test -d venv || python3 -m venv venv
	@source venv/bin/activate
	@pip install '.[dev]'

.PHONY: test
test: venv
	@python -m pytest

.PHONY: clean
clean:
	@rm -rf venv
	@find -iname "*.pyc" -delete
