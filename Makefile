.PHONY: build
build: venv pre-commit
	@pip install .
	@python setup.py build

.PHONY: lint
lint: pre-commit
	@ruff check .

.PHONY: pre-commit
pre-commit:
	@command -v ruff >/dev/null || pip install ruff

.PHONY: venv
venv:
	@test -d venv || python3 -m venv venv
	@source venv/bin/activate
	@pip install '.[dev]' 

.PHONY: test-drone
test-ci:
	@pip install '.[dev]' 
	@make test

.PHONY: test
test:
	@command -v coverage >/dev/null || pip install coverage
	@python -m pytest tests/*_test.py

.PHONY: clean
clean:
	@rm -rf venv
	@find -iname "*.pyc" -delete
