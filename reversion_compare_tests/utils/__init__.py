# coding: utf-8

"""
    unittests
    ~~~~~~~~~

    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import shutil


def cleanup_temp(temp_dir):
    print("\nCleanup %r: " % temp_dir, end="")
    try:
        shutil.rmtree(temp_dir)
    except (OSError, IOError) as err:
        print("Error: %s" % err)
    else:
        print("OK")
