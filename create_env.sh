#!/usr/bin/env bash

DESTINATION=$(pwd)/.virtualenv
REQ_FILE=$(pwd)/requirements-dev.txt

(
    set -e
    set -x

    python3 --version
    python3 -Im venv --without-pip ${DESTINATION}
)
(
    source ${DESTINATION}/bin/activate
    set -x
    python3 -m ensurepip
)
if [ "$?" == "0" ]; then
    echo "pip installed, ok"
else
    echo "ensurepip doesn't exist, use get-pip.py"
    (
        set -e
        source ${DESTINATION}/bin/activate
        set -x
        cd ${DESTINATION}/bin
        wget https://bootstrap.pypa.io/get-pip.py
        ${DESTINATION}/bin/python get-pip.py
    )
fi
(
    set -e
    source ${DESTINATION}/bin/activate
    set -x
    cd ${DESTINATION}/bin/

    pip3 install --upgrade pip
    pip3 install --upgrade -r ${REQ_FILE}
)
