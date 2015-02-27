#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import os
import sys

from setuptools import setup, find_packages

from reversion_compare import VERSION_STRING


PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


# convert creole to ReSt on-the-fly, see also:
# https://code.google.com/p/python-creole/wiki/UseInSetup
try:
    from creole.setup_utils import get_long_description
except ImportError as err:
    if "check" in sys.argv or "register" in sys.argv or "sdist" in sys.argv or "--long-description" in sys.argv:
        raise ImportError("%s - Please install python-creole >= v0.8 - e.g.: pip install python-creole" % err)
    long_description = None
else:
    long_description = get_long_description(PACKAGE_ROOT)


def get_authors():
    try:
        with open(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r") as f:
            authors = [l.strip(" *\r\n") for l in f if l.strip().startswith("*")]
    except Exception as err:
        authors = "[Error: %s]" % err
    return authors


setup(
    name='django-reversion-compare',
    version=VERSION_STRING,
    description='history compare for django-reversion',
    keywords=["django", "django-reversion", "reversion", "diff", "compare"],
    long_description=long_description,
    author=get_authors(),
    maintainer="Jens Diemer",
    maintainer_email="django-reversion-compare@jensdiemer.de",
    url='https://github.com/jedie/django-reversion-compare/',
    download_url='http://pypi.python.org/pypi/django-reversion-compare/',
    packages=find_packages(),
    include_package_data=True,  # include package data under svn source control
    install_requires=[
        "Django>=1.7,<1.8",
        "django-reversion>=1.8",
    ],
    tests_require=[
        "django-tools",  # https://github.com/jedie/django-tools/
    ],
    zip_safe=False,
    classifiers=[
#        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
#        "Intended Audience :: Education",
#        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        'Framework :: Django',
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ],
    test_suite="runtests.run_tests",
)
