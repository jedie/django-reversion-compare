#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid
    ~~~~~~~

    run all tests:

    (PyLucid_env) ~/PyLucid_env/src/pylucid $ ./runtests.py

    run only some tests, e.g.:

    (PyLucid_env) ~/PyLucid_env/src/pylucid $ ./runtests.py tests.test_file
    (PyLucid_env) ~/PyLucid_env/src/pylucid $ ./runtests.py tests.test_file.test_class
    (PyLucid_env) ~/PyLucid_env/src/pylucid $ ./runtests.py tests.test_file.test_class.test_method

    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import shutil

import django
from django.conf import settings
from django.test.utils import get_runner

# from pylucid_installer.page_instance_template import example_project
#
# # Made the 'example_project' importable to use it in unittests
# sys.path.append(
#     os.path.join(os.path.dirname(example_project.__file__), os.pardir)
# )

def cleanup_temp(temp_dir):
    print("\nCleanup %r: " % temp_dir, end="")
    try:
        shutil.rmtree(temp_dir)
    except (OSError, IOError) as err:
        print("Error: %s" % err)
    else:
        print("OK")


def run_tests(test_labels=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    if test_labels is None:
        test_labels = ['tests']
    failures = test_runner.run_tests(test_labels)

    cleanup_temp(settings.TEMP_DIR)

    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests(test_labels = sys.argv[1:])

