#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file mainly exists to allow python setup.py test to work.
    You can also call it directly or call:
        ./setup.py test

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'reversion_compare_test_project.settings'
test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, test_dir)

from django.conf import settings
from django.test.utils import get_runner, setup_test_environment
from django.test.simple import DjangoTestSuiteRunner


class TestSuiteRunner(DjangoTestSuiteRunner):
    """
    FIXME: startup south migrate here, because settings.SOUTH_TESTS_MIGRATE doesn't work.
    http://south.readthedocs.org/en/latest/unittests.html
    """
    def setup_databases(self, **kwargs):
        result = super(TestSuiteRunner, self).setup_databases()
        from django.core import management
        management.call_command("migrate", verbosity=self.verbosity - 1, traceback=True, interactive=False)
        return result


def runtests():
#    from django.core import management
#    management.call_command("test", "reversion_compare", verbosity=2, traceback=True, interactive=False)

#    TestRunner = get_runner(settings)
#    test_runner = TestRunner(verbosity=2, interactive=True)

    test_runner = TestSuiteRunner(verbosity=2, interactive=True)

    failures = test_runner.run_tests(['reversion_compare'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()
