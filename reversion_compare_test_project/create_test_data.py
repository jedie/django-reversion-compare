#!/usr/bin/env python
# coding: utf-8

"""
    insert the test data from unittests to the test project database
    so you can easy play with them in a real admin page ;)
    
    this script will be called from "reset.sh"
    
    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = "reversion_compare_test_project.settings"

import reversion
from reversion.models import Revision, Version

from reversion_compare.tests import TestData


if __name__ == "__main__":
    Revision.objects.all().delete()
    Version.objects.all().delete()
    
    TestData(verbose = True).create_all()

    print("\n+++ Test data from unittests created +++")
