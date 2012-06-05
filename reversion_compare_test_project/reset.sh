#!/bin/bash

set -x

rm -i test.db3
./manage.py syncdb --all --noinput
./manage.py migrate --fake
./manage.py createsuperuser --username=test --email=test@example.tld
./create_test_data.py