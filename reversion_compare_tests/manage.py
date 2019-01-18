#!/usr/bin/env python
import os
import sys

from .utils import cleanup_temp


def cli(arguments):
    os.environ["DJANGO_SETTINGS_MODULE"] = "reversion_compare_tests.settings"
    print("\nUse DJANGO_SETTINGS_MODULE=%r" % os.environ["DJANGO_SETTINGS_MODULE"])
    from django.core.management import execute_from_command_line

    old_cwd = os.getcwd()
    try:
        execute_from_command_line(arguments)
    finally:
        if not os.environ.get("RUN_MAIN"):
            # Cleanup only in the outer run process.
            # RUN_MAIN will be set in django.utils.autoreload
            os.chdir(old_cwd)
            from django.conf import settings

            cleanup_temp(settings.UNITTEST_TEMP_PATH)


def start_test_server():
    cli(arguments=[sys.argv[0], "run_testserver"])


if __name__ == "__main__":
    cli(sys.argv)
