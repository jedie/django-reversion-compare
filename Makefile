SHELL := /bin/bash
MAX_LINE_LENGTH := 119

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -_]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-poetry:
	@if [[ "$(shell poetry --version 2>/dev/null)" == *"Poetry"* ]] ; \
	then \
		echo "Found Poetry, ok." ; \
	else \
		echo 'Please install poetry first, with e.g.:' ; \
		echo 'make install-poetry' ; \
		exit 1 ; \
	fi

install-poetry: ## install or update poetry via pip
	pip3 install -U poetry

install: check-poetry ## install via poetry
	poetry install

update: check-poetry ## Update the dependencies as according to the pyproject.toml file
	poetry update

lint: ## Run code formatters and linter
	poetry run flynt --fail-on-change --line-length=${MAX_LINE_LENGTH} reversion_compare reversion_compare_tests
	poetry run isort --check-only .
	poetry run flake8 reversion_compare reversion_compare_tests

fix-code-style: ## Fix code formatting
	poetry run flynt --line-length=${MAX_LINE_LENGTH} reversion_compare reversion_compare_tests
	poetry run autopep8 --aggressive --aggressive --in-place --recursive reversion_compare reversion_compare_tests
	poetry run isort .

pyupgrade:  ## Run pyupgrade
	poetry run pyupgrade --exit-zero-even-if-changed --py3-plus --py36-plus --py37-plus --py38-plus `find . -name "*.py" -type f ! -path "./.tox/*" ! -path "./htmlcov/*" ! -path "*/volumes/*" 2>/dev/null`

tox-listenvs: check-poetry ## List all tox test environments
	poetry run tox --listenvs

tox: check-poetry ## Run pytest via tox with all environments
	poetry run tox

pytest: check-poetry ## Run pytest
	poetry run pytest

update-rst-readme: ## update README.rst from README.creole
	poetry run update_rst_readme

publish: ## Release new version to PyPi
	poetry run publish

run-test-server: ## Start Django dev server with the test project
	./manage.sh run_testserver

makemessages: ## Make and compile locales message files
	./manage.sh makemessages --all --no-location --no-obsolete --ignore=htmlcov --ignore=".tox*" --ignore=volumes
	./manage.sh compilemessages --ignore=htmlcov --ignore=".tox*" --ignore=volumes

.PHONY: help install lint fix pytest publish
