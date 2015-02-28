#!/bin/sh
(
    set -x
    ./tests/manage.py run_testserver
)