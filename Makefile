SHELL := /bin/bash
MAX_LINE_LENGTH := 119

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

lint: ## Run code formatters and linter
	.virtualenv/bin/flynt --fail-on-change --line_length=${MAX_LINE_LENGTH} reversion_compare reversion_compare_tests
	.virtualenv/bin/isort --check-only --recursive reversion_compare reversion_compare_tests
	.virtualenv/bin/flake8 reversion_compare reversion_compare_tests

fix-code-style: ## Fix code formatting
	.virtualenv/bin/flynt --line_length=${MAX_LINE_LENGTH} reversion_compare reversion_compare_tests
	.virtualenv/bin/isort --apply --recursive reversion_compare reversion_compare_tests
	.virtualenv/bin/autopep8 --ignore-local-config --max-line-length=${MAX_LINE_LENGTH} --aggressive --aggressive --in-place --recursive reversion_compare reversion_compare_tests

tox:
	.virtualenv/bin/tox