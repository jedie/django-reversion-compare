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

source ${DESTINATION}/bin/activate
set -e

cd ${DESTINATION}

(
    ./bin/pip3 install --upgrade pip
    ./bin/pip3 install --upgrade -r ${REQ_FILE}
)
(
    # install "black" - https://github.com/ambv/black

    echo -e "\nblack requires Python 3.6.0+"
    echo -e "Ignore errors if you are on 3.5 ;)\n"
    set +e
    set -x
    ./bin/pip3 install --upgrade black
)
