#!/usr/bin/env python
# coding: utf-8

import os,sys

BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1,os.path.join(BASE, "../"))

os.environ['DJANGO_SETTINGS_MODULE'] = "reversion_compare_test_project.settings"

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
