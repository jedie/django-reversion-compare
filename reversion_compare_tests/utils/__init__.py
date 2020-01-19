# coding: utf-8

"""
    unittests
    ~~~~~~~~~

    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import shutil


def cleanup_temp(temp_dir):
    print(f"\nCleanup {temp_dir!r}: ", end="")
    try:
        shutil.rmtree(temp_dir)
    except (OSError, IOError) as err:
        print(f"Error: {err}")
    else:
        print("OK")
