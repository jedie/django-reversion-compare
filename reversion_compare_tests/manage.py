#!/usr/bin/env python3
import os
import shutil
import sys


def cleanup_temp(temp_dir):
    print(f"\nCleanup {temp_dir!r}: ", end="")
    try:
        shutil.rmtree(temp_dir)
    except OSError as err:
        print(f"Error: {err}")
    else:
        print("OK")


def cli():
    os.environ["DJANGO_SETTINGS_MODULE"] = "reversion_compare_tests.settings"
    print(f"\nUse DJANGO_SETTINGS_MODULE={os.environ['DJANGO_SETTINGS_MODULE']!r}")
    from django.core.management import execute_from_command_line

    old_cwd = os.getcwd()
    print(' '.join(sys.argv))
    try:
        execute_from_command_line(sys.argv)
    finally:
        if not os.environ.get("RUN_MAIN"):
            # Cleanup only in the outer run process.
            # RUN_MAIN will be set in django.utils.autoreload
            os.chdir(old_cwd)
            from django.conf import settings

            cleanup_temp(settings.UNITTEST_TEMP_PATH)


def start_test_server():
    sys.argv = [__file__, "run_testserver"]
    cli()


if __name__ == "__main__":
    cli()
