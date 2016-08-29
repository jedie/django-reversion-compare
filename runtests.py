#!/usr/bin/env python
# coding: utf-8

"""
    run unittests
    ~~~~~~~~~~~~~

    run all tests:

    ./runtests.py

    run only some tests, e.g.:

    ./runtests.py tests.test_file
    ./runtests.py tests.test_file.test_class
    ./runtests.py tests.test_file.test_class.test_method

    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

from tests.test_utils import cleanup_temp


def run_tests(test_labels=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    if test_labels is None:
        test_labels = ['tests']
    failures = test_runner.run_tests(test_labels)

    cleanup_temp(settings.UNITTEST_TEMP_PATH)

    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests(test_labels = sys.argv[1:])

