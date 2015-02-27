#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    print("\nUse DJANGO_SETTINGS_MODULE=%r" % os.environ["DJANGO_SETTINGS_MODULE"])

    from django.core.management import execute_from_command_line

    old_cwd = os.getcwd()
    try:
        execute_from_command_line(sys.argv)
    finally:
        os.chdir(old_cwd)
        from django.conf import settings
        from tests.test_utils import cleanup_temp
        cleanup_temp(settings.UNITTEST_TEMP_PATH)