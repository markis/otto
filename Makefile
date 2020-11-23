.PHONY: build
build: venv pre-commit
	@pip install .
	@python setup.py build

.PHONY: lint
lint: pre-commit
	@pre-commit run --all-files

.PHONY: pre-commit
pre-commit:
	@command -v pre-commit >/dev/null || pip install pre-commit
	@pre-commit install -f --install-hooks

.PHONY: venv
venv:
	@test -d otto-venv || virtualenv -p python3 otto-venv
	@source otto-venv/bin/activate
	@pip install -Ur requirements-dev.txt

.PHONY: test-drone
test-drone:
	@pip install -Ur requirements-dev.txt
	@make test

.PHONY: test
test:
	@command -v coverage >/dev/null || pip install coverage
	@coverage run  --source="otto/" -m py.test tests/*_test.py
	@coverage report -m

.PHONY: clean
clean:
	@rm -rf otto-venv
	@find -iname "*.pyc" -delete
