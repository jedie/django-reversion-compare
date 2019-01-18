#!/usr/bin/env bash

VIRTUALENV=.virtualenv

if [[ ! -d ${VIRTUALENV} ]]; then
    echo -e "ERROR: Virtualenv not found here: '${VIRTUALENV}'"
    exit -1
fi

source ${VIRTUALENV}/bin/activate
set -ex

# https://github.com/ambv/black#command-line-options
${VIRTUALENV}/bin/black --line-length=119 --safe ./reversion_compare/
${VIRTUALENV}/bin/black --line-length=119 --safe ./reversion_compare_tests/
