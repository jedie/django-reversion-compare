#!/usr/bin/env bash

set -e

BASE_PATH=$(pwd)
VENV_DIR=.virtualenv
REQ_FILE=${BASE_PATH}/requirements-dev.txt

cd ${BASE_PATH}

(
    set -x
    python3 --version
    python3 -Im venv --without-pip ${VENV_DIR}
)
(
    source ${VENV_DIR}/bin/activate
    set -x
    python3 -m ensurepip
)
if [ "$?" == "0" ]; then
    echo "pip installed, ok"
else
    echo "ensurepip doesn't exist, use get-pip.py"
    (
        set -e
        source ${VENV_DIR}/bin/activate
        set -x
        cd ${VENV_DIR}/bin
        wget https://bootstrap.pypa.io/get-pip.py
        ./python3 get-pip.py
    )
fi

source ${VENV_DIR}/bin/activate
set -e

(
    set -x

    # upgrade pip:
    ${VENV_DIR}/bin/pip3 install --upgrade pip

    # install git clone as editable:
    ${VENV_DIR}/bin/pip3 install -e .

    # install requirements.txt:
    ${VENV_DIR}/bin/pip3 install --upgrade -r ${REQ_FILE}
)
