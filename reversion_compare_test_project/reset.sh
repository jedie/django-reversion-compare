#!/bin/bash

set -x

rm -i test.db3
./manage.py syncdb --noinput --migrate
./manage.py createsuperuser --username=test --email=test@example.tld