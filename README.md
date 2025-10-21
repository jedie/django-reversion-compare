# django-reversion-compare

[![tests](https://github.com/jedie/django-reversion-compare/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/django-reversion-compare/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/django-reversion-compare/branch/main/graph/badge.svg)](https://app.codecov.io/github/jedie/django-reversion-compare)
[![django-reversion-compare @ PyPi](https://img.shields.io/pypi/v/django-reversion-compare?label=django-reversion-compare%20%40%20PyPi)](https://pypi.org/project/django-reversion-compare/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-reversion-compare)](https://github.com/jedie/django-reversion-compare/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/django-reversion-compare)](https://github.com/jedie/django-reversion-compare/blob/main/LICENSE)

**django-reversion-compare** is an extension to [django-reversion](https://github.com/etianen/django-reversion/) that provides a history compare view to compare two versions of a model which is under reversion.

Comparing model versions is not a easy task. Maybe there are different view how this should looks like.
This project will gives you a generic way to see whats has been changed.

Many parts are customizable by overwrite methods or subclassing, see above.


## Installation

Just use:
```
pip install django-reversion-compare
```

### Setup

Add **reversion_compare** to **INSTALLED_APPS** in your settings.py, e.g.:
```
INSTALLED_APPS = (
    'django...',
    ...
    'reversion', # https://github.com/etianen/django-reversion
    'reversion_compare', # https://github.com/jedie/django-reversion-compare
    ...
)

# Add reversion models to admin interface:
ADD_REVERSION_ADMIN=True
# optional settings:
REVERSION_COMPARE_FOREIGN_OBJECTS_AS_ID=False
REVERSION_COMPARE_IGNORE_NOT_REGISTERED=False
```

### Usage

Inherit from **CompareVersionAdmin** instead of **VersionAdmin** to get the comparison feature.

admin.py e.g.:
```
from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from my_app.models import ExampleModel

@admin.register(ExampleModel)
class ExampleModelAdmin(CompareVersionAdmin):
    pass
```

If you're using an existing third party app, then you can add patch django-reversion-compare into
its admin class by using the **reversion_compare.helpers.patch_admin()** method. For example, to add
version control to the built-in User model:
```
from reversion_compare.helpers import patch_admin

patch_admin(User)
```

e.g.: Add django-cms Page model:
```
from cms.models.pagemodel import Page
from reversion_compare.helpers import patch_admin


# Patch django-cms Page Model to add reversion-compare functionality:
patch_admin(Page)
```

### Customize

It's possible to change the look for every field or for a entire field type.
You must only define a methods to your admin class with this name scheme:


* `"compare_%s" % field_name`
* `"compare_%s" % field.get_internal_type()`

If there is no method with this name scheme, the `fallback_compare()` method will be used.

An example for specifying a compare method for a model field by name:
```
class YourAdmin(CompareVersionAdmin):
    def compare_foo_bar(self, obj_compare):
        """ compare the foo_bar model field """
        return "%r <-> %r" % (obj_compare.value1, obj_compare.value2)
```

and example using **patch_admin** with custom version admin class:
```
patch_admin(User, AdminClass=YourAdmin)
```

## Class Based View

Beyond the Admin views, you can also create a Class Based View for displaying and comparing version
differences. This is a single class-based-view that either displays the list of versions to select
for an object or displays both the versions **and** their differences (if the versions to be compared
have been selected). This class can be used just like a normal DetailView:

More information about this can be found in DocString of:


* [HistoryCompareDetailView](https://github.com/jedie/django-reversion-compare/blob/main/reversion_compare/views.py)

The `make run-test-server` test project contains a Demo, use the links under:
```
HistoryCompareDetailView Examples:
```

## Screenshots

Here some screenshots of django-reversion-compare:

----

How to select the versions to compare:

![django-reversion-compare_v0_1_0-01.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120508_django-reversion-compare_v0_1_0-01.png "django-reversion-compare_v0_1_0-01.png")

----

from **v0.1.0**: DateTimeField compare (last update), TextField compare (content) with small changes and a ForeignKey compare (child model instance was added):

![django-reversion-compare_v0_1_0-02.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120508_django-reversion-compare_v0_1_0-02.png "django-reversion-compare_v0_1_0-02.png")

----

from **v0.1.0**: Same as above, but the are more lines changed in TextField and the ForeignKey relation was removed:

![django-reversion-compare_v0_1_0-03.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120508_django-reversion-compare_v0_1_0-03.png "django-reversion-compare_v0_1_0-03.png")

----

Example screenshot from **v0.3.0**: a many-to-many field compare (friends, hobbies):

![django-reversion-compare_v0_3_0-01.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120516_django-reversion-compare_v0_3_0-01.png "django-reversion-compare_v0_3_0-01.png")


* In the first line, the m2m object has been changed.
* line 2: A m2m object was deleted
* line 3: A m2m object was removed from this entry (but not deleted)
* line 4: This m2m object has not changed

## create developer environment

We use [manage_django_project](https://github.com/jedie/manage_django_project), so you just need to clone the sources and call `manage.py` to start hacking.

e.g.:
```
~$ git clone https://github.com/jedie/django-reversion-compare.git
~$ cd django-reversion-compare

# Just call manage.py and the magic happen:
~/django-reversion-compare$ ./manage.py

# start local dev. web server:
~/django-reversion-compare$ ./manage.py run_dev_server

# run tests:
~/django-reversion-compare$ ./manage.py test
# or with coverage
~/django-reversion-compare$ ./manage.py coverage
# or via tox:
~/django-reversion-compare$ ./manage.py tox p
```


## Backwards-incompatible changes

### v0.16.0

We use https://github.com/jedie/manage_django_project to manage the dev venv
and we switch to `main` branch.

You must reinit your dev setup.


### v0.12.0

Google "diff-match-patch" is now mandatory and not optional.


## Version compatibility

| Reversion-Compare | django-reversion | Django             | Python                                         |
|-------------------|------------------|--------------------|------------------------------------------------|
| >=v0.19.0         | v6.0             | v4.2, v5.1, v5.2   | v3.11, v3.12, v3.13                            |
| >=v0.18.0         | v5.1             | v4.2, v5.0, v5.1   | v3.11, v3.12                                   |
| >=v0.17.0         | v5.0             | (v3.2), v4.2, v5.0 | (v3.9), v3.10, v3.11, v3.12                    |
| >=v0.16.0         | v3.0             | v3.2, v4.1, v4.2   | v3.9, v3.10, v3.11                             |
| >=v0.15.0         | v3.0             | v2.2, v3.2, v4.0   | v3.7, v3.8, v3.9                               |
| >=v0.13.0         | v3.0             | v2.2, v3.0, v3.1   | v3.7, v3.8, v3.9                               |
| >=v0.10.0         | v3.0             | v2.2, v3.0         | v3.6, v3.7, v3.8, pypy3                        |
| >=v0.9.0          | v2.0             | v2.2, v3.0         | v3.6, v3.7, v3.8, pypy3                        |
| >=v0.8.6          | v2.0             | v1.11, v2.0        | v3.5, v3.6, v3.7, pypy3                        |
| >=v0.8.4          | v2.0             | v1.8, v1.11, v2.0  | v3.5, v3.6, pypy3                              |
| >=v0.8.3          | v2.0             | v1.8, v1.11        | v3.5, v3.6, pypy3                              |
| v0.8.x            | v2.0             | v1.8, v1.10, v1.11 | v2.7, v3.4, v3.5, v3.6 (only with Django 1.11) |
| >=v0.7.2          | v2.0             | v1.8, v1.9, v1.10  | v2.7, v3.4, v3.5                               |
| v0.7.x            | v2.0             | v1.8, v1.9         | v2.7, v3.4, v3.5                               |
| v0.6.x            | v1.9, v1.10      | v1.8, v1.9         | v2.7, v3.4, v3.5                               |
| >=v0.5.2          | v1.9             | v1.7, v1.8         | v2.7, v3.4                                     |
| >=v0.4            | v1.8             | v1.7               | v2.7, v3.4                                     |
| <v0.4             | v1.6             | v1.4               | v2.7                                           |

These are the unittests variants. See also: [/noxfile.py](https://github.com/jedie/django-reversion-compare/blob/main/noxfile.py)
Maybe other versions are compatible, too.

## Changelog

[comment]: <> (✂✂✂ auto generated history start ✂✂✂)

* [v0.19.1](https://github.com/jedie/django-reversion-compare/compare/v0.19.0...v0.19.1)
  * 2025-10-21 - Apply manageprojects updates + update requirements
* [v0.19.0](https://github.com/jedie/django-reversion-compare/compare/v0.18.1...v0.19.0)
  * 2025-09-25 - Cleanup and update README
  * 2025-09-25 - fix packaging: Add hatchling
  * 2025-09-25 - Bugfix CI
  * 2025-09-25 - apply manageprojects updates
* [v0.18.1](https://github.com/jedie/django-reversion-compare/compare/v0.18.0...v0.18.1)
  * 2024-09-10 - Bugfix packaging: We use rich in production code
* [v0.18.0](https://github.com/jedie/django-reversion-compare/compare/v0.17.0...v0.18.0)
  * 2024-09-10 - modernized code
  * 2024-09-10 - Update test matrix and requirements
  * 2024-09-10 - Apply manageprojects updates
  * 2024-09-10 - Update requirements
  * 2024-05-21 - fix time in snapshots
  * 2024-05-21 - Apply manageprojects update
  * 2024-02-20 - Update README.md

<details><summary>Expand older history entries ...</summary>

* [v0.17.0](https://github.com/jedie/django-reversion-compare/compare/v0.16.2...v0.17.0)
  * 2024-02-20 - Enhance diff
  * 2024-02-20 - Update requirements
  * 2024-01-17 - mamageprojects updates + update requirements
  * 2023-12-17 - Update tests.yml
  * 2023-12-17 - Configure unittests via "load_tests Protocol"
  * 2023-12-17 - Apply manageproject updates
  * 2023-11-07 - Add Python 3.12 to text matrix + project upgrade
  * 2023-05-23 - Bump requests from 2.28.2 to 2.31.0
* [v0.16.2](https://github.com/jedie/django-reversion-compare/compare/v0.16.1...v0.16.2)
  * 2023-05-08 - Bugfix RegistrationError: <Model> has not been registered with django-reversion
  * 2023-05-08 - Update requirements
  * 2023-04-28 - Fix link for CBV
* [v0.16.1](https://github.com/jedie/django-reversion-compare/compare/v0.16.0...v0.16.1)
  * 2023-04-08 - Fix wrong README and release as v0.16.1
  * 2023-04-08 - Use new "update_req" command from manage_django_project v0.4.0
  * 2023-04-08 - Fix #195 move "diff-match-patch" not normal dependencies section
* [v0.16.0](https://github.com/jedie/django-reversion-compare/compare/v0.15.0...v0.16.0)
  * 2023-04-07 - tests against different Django versions
  * 2023-04-07 - Update README.md
  * 2023-04-07 - +license = {text = "GPL-3.0-or-later"}
  * 2023-04-07 - Update pyproject.toml
  * 2023-04-06 - Refactor project setup
  * 2023-04-07 - Update requirements
  * 2023-04-06 - test against newer Django and Python
  * 2022-08-23 - Cache .cache
  * 2022-08-23 - WIP: Replace README.creole with README.md
  * 2022-08-12 - update project setup
  * 2022-07-05 - Bump django from 3.2.13 to 3.2.14
  * 2022-05-16 - update tox settings
  * 2022-05-29 - Fix wrong Link in README
  * 2022-05-16 - Use darker
  * 2022-02-10 - Bump django from 3.2.11 to 3.2.12
* [v0.15.0](https://github.com/jedie/django-reversion-compare/compare/v0.14.1...v0.15.0)
  * 2022-01-27 - remove Python 3.7 and Django 4.0 from tox config
  * 2022-01-27 - Bugfix model choice fields (e.g.: django-countries fields)
  * 2022-01-27 - Construct a test model with django-countries model fields for #162
  * 2022-01-27 - Remove test project migration files
  * 2022-01-27 - update README
  * 2022-01-27 - Fix linting by code cleanup
  * 2022-01-27 - Activate test_missing_migrations()
  * 2022-01-27 - Bugfix flynt call
  * 2022-01-27 - Update to f-strings
  * 2022-01-27 - remove temp path usage
  * 2022-01-27 - setup test project logging
  * 2022-01-27 - Add poetry.lock
  * 2022-01-27 - Text with Django 2.2, 3.2 and 4.0
  * 2022-01-27 - update test project settings
  * 2022-01-27 - Update to new bx_django_utils
  * 2021-12-19 - switched ugettext to gettext
* [v0.14.1](https://github.com/jedie/django-reversion-compare/compare/v0.14.0...v0.14.1)
  * 2021-07-19 - Add VersionAdmin "content_type" to raw_id_fields
  * 2021-06-15 - Enable Diff-Match-Patch "checklines" mode for better diffs
  * 2021-04-05 - Update ci.yml
  * 2021-03-18 - One more list_select_related optimization
  * 2021-03-18 - list_select_related to speed up the list page
  * 2021-03-18 - Use raw_id_fields, refs #152
  * 2021-02-18 - Fix line breaks on long lines in diff
* [v0.14.0](https://github.com/jedie/django-reversion-compare/compare/v0.13.1...v0.14.0)
  * 2021-02-24 - Fix #148 add a compare fallback
  * 2021-02-24 - set "USE_TZ = True" in test project
  * 2021-02-24 - Fix translations in test project
* [v0.13.1](https://github.com/jedie/django-reversion-compare/compare/v0.13.0...v0.13.1)
  * 2021-02-04 - update README
  * 2021-02-04 - Don't use DebugCacheLoader
  * 2021-02-04 - Add demo links to "HistoryCompareDetailView" in test project
  * 2021-02-04 - prepare v0.13.1 release
  * 2021-02-04 - fix code style
  * 2021-02-04 - Multiline diff formatting improvements #137
  * 2021-02-04 - push: branches: [master]
  * 2021-02-04 - +[gh-actions]
  * 2021-02-04 - .github/workflows/{pythonapp.yml => ci.yml}
  * 2021-02-04 - update github actions
  * 2021-01-27 - Fix django.conf.urls.url() is deprecated
  * 2020-12-23 - don't publish if test fails
* [v0.13.0](https://github.com/jedie/django-reversion-compare/compare/v0.12.2...v0.13.0)
  * 2020-12-23 - remove travis stuff
  * 2020-12-23 - Activate django-debug-toolbar in test project
  * 2020-12-23 - update changelog in README
  * 2020-12-23 - cleanup some f-strings
  * 2020-12-23 - add "make pyupgrade"
  * 2020-12-23 - update github actions
  * 2020-12-23 - fix imports code style
  * 2020-12-23 - remove django warning
  * 2020-12-23 - recompile messages
  * 2020-12-23 - refactor test imports
  * 2020-12-23 - update project setup
  * 2020-12-23 - fix "make help"
  * 2020-12-23 - python = ">=3.7,<4.0.0"
  * 2020-12-23 - update test_assert_rst_readme()
  * 2020-12-23 - cleanup
  * 2020-12-23 - remove .travis.yml
  * 2020-10-26 - Two typos in readme.rst
  * 2020-08-10 - Remove Django from dependencies, update tox matrix
  * 2020-08-10 - Remove deprecated pytest option
  * 2020-07-01 - Replace deprecated force_text with force_str
  * 2020-07-01 - Switch remaining % formatting to f-strings
* [v0.12.2](https://github.com/jedie/django-reversion-compare/compare/v0.12.1...v0.12.2)
  * 2020-03-24 - release v0.12.2
  * 2020-03-24 - Update AUTHORS
  * 2020-03-24 - Added revert button on compare view
  * 2020-03-20 - remove code for support old django-reversion releases
* [v0.12.1](https://github.com/jedie/django-reversion-compare/compare/v0.12.0...v0.12.1)
  * 2020-03-20 - release v0.12.1
  * 2020-03-20 - remove obsolete django.VERSION < (1, 10) code
  * 2020-03-20 - rename django admin title and branding
  * 2020-03-20 - Test project used a "auto login test user" middleware
  * 2020-03-17 - Add Django version 3.0 to the project dependencies
* [v0.12.0](https://github.com/jedie/django-reversion-compare/compare/v0.11.0...v0.12.0)
  * 2020-03-12 - update example styles
  * 2020-03-12 - test 0.12.0.rc1
  * 2020-03-12 - update Travis CI config
  * 2020-03-12 - fix lint and activate&update variant model tests
  * 2020-03-12 - update README
  * 2020-03-12 - Bump to v0.12.0
  * 2020-03-12 - Make diff-match-patch mandatory and auto switch between diffs via size
* [v0.11.0](https://github.com/jedie/django-reversion-compare/compare/v0.10.0...v0.11.0)
  * 2020-03-12 - update README
  * 2020-03-12 - fix lint + code cleanup
  * 2020-03-12 - less verbose pytest
  * 2020-03-12 - use @pytest.mark.skipif()
  * 2020-03-12 - Use own html pretty function instead of diff_match_patch.diff_prettyHtml
  * 2020-03-12 - "diff-match-patch" as optional dependencies
  * 2020-03-12 - Fix Link: code.google.com/p/google-diff-match-patch -> github.com/google/diff-match-patch
  * 2020-03-05 - bugfix django requirement
  * 2020-03-05 - remove unused import
  * 2020-02-19 - merge code by using test code from poetry-publish
* [v0.10.0](https://github.com/jedie/django-reversion-compare/compare/v0.9.1...v0.10.0)
  * 2020-02-19 - lock + show --tree before install to find install problems:
  * 2020-02-19 - don't test README if dev or rc versions
  * 2020-02-19 - fixup! Expand dependencies version ranges to fix #120
  * 2020-02-19 - update README
  * 2020-02-19 - Expand dependencies version ranges to fix #120
  * 2020-02-17 - Update README.creole
* [v0.9.1](https://github.com/jedie/django-reversion-compare/compare/v0.9.0...v0.9.1)
  * 2020-02-16 - apply isort
  * 2020-02-14 - Skip isort for linting.
  * 2020-02-14 - Apply pyupgrade and fix/update some f-strings
  * 2020-02-14 - fix code style
  * 2020-02-13 - update README
  * 2020-02-13 - add some basic tests
  * 2020-02-13 - Update run test project server
  * 2020-02-13 - bugfix import
  * 2020-02-13 - update models.CommaSeparatedIntegerField()
  * 2020-02-13 - update test project settings
  * 2020-02-13 - update pytest config
  * 2020-02-13 - Upload coverage report after test
  * 2020-02-13 - update django-tools
  * 2020-02-13 - +reversion_compare_tests/test_project_setup.py
  * 2020-02-13 - don't publish if README is not up-to-date
  * 2020-02-13 - flake8: remove exceptions
  * 2020-02-11 - use poetry
  * 2020-02-01 - Update pythonapp.yml
* [v0.9.0](https://github.com/jedie/django-reversion-compare/compare/v0.8.7...v0.9.0)
  * 2020-01-19 - Update README.creole
  * 2020-01-19 - use tox-gh-actions
  * 2020-01-19 - fix code style errors
  * 2020-01-19 - update Travis CI config
  * 2020-01-19 - Bugfix tox.ini
  * 2020-01-19 - setup github actions
  * 2020-01-19 - apply autopep8
  * 2020-01-19 - remove __future__ imports
  * 2020-01-19 - fix imports with isort
  * 2020-01-19 - convert old format to f-strings via flynt
  * 2020-01-19 - Add Makefile, but only for lint + fix-code-style with flynt, isort, flake8 and autopep8
  * 2020-01-19 - Test with Python 3.8 and Django 3.0, too
  * 2020-01-19 - Update AUTHORS
  * 2020-01-06 - actually check if model is registered
  * 2019-11-05 - Show username and full name from custom user model
  * 2019-10-15 - Remove python2 compatibility decorators
  * 2019-07-17 - Fix django-suit NoneType is not iterable
* [v0.8.7](https://github.com/jedie/django-reversion-compare/compare/v0.8.6...v0.8.7)
  * 2020-01-06 - release v0.8.7
  * 2020-01-06 - Update README.creole and AUTHORS
  * 2020-01-06 - Update README.creole
  * 2019-12-13 - add option to ignore not registered models
  * 2019-01-18 - +skip_missing_interpreters = true
  * 2019-01-18 - remove some obsolete code parts
  * 2019-01-18 - update classes
  * 2019-01-18 - bugfix "create_env.sh": install reversion_compare as editable
  * 2019-01-18 - just run black
  * 2019-01-18 - add black.sh
  * 2019-01-18 - + install black
  * 2019-01-18 - update existing virtualenv
* [v0.8.6](https://github.com/jedie/django-reversion-compare/compare/v0.8.5...v0.8.6)
  * 2019-01-04 - python 3.7 works fine
  * 2019-01-04 - WIP: fix travis config
  * 2019-01-04 - update README and set version==0.8.6
  * 2019-01-04 - +Lisák, Peter
  * 2019-01-04 - Run tests: Skip Django v1.8 and add Python v3.7
  * 2019-01-04 - add 'create_env.sh' for easier create a dev. virtualenv
  * 2019-01-04 - Delete .project
  * 2019-01-04 - Use .pk instead of .id when referring to related object.
* [v0.8.5](https://github.com/jedie/django-reversion-compare/compare/v0.8.4...v0.8.5)
  * 2018-09-13 - some adds
  * 2018-09-13 - +Framework :: Django :: 2.0
  * 2018-09-13 - only code format
  * 2018-08-20 - Update README.creole
  * 2018-07-19 - speed up delete checking, bump version
* [v0.8.4](https://github.com/jedie/django-reversion-compare/compare/v0.8.3...v0.8.4)
  * 2018-03-15 - update "publish" code
  * 2018-03-15 - Update README.creole
  * 2017-12-29 - Update AUTHORS
  * 2017-12-29 - Add Django 2.0 compatibility
* [v0.8.3](https://github.com/jedie/django-reversion-compare/compare/v0.8.2...v0.8.3)
  * 2017-12-21 - add author_email to remove warning
  * 2017-12-20 - + coveralls
  * 2017-12-20 - coverage
  * 2017-12-20 - test with pypy3
  * 2017-12-20 - cleanup + update README
  * 2017-12-20 - rafactor tests
  * 2017-12-20 - reversion_compare_tests/{test_utils => utils}/
  * 2017-12-20 - Update travis/tox config and don't test with unsupported django versions
  * 2017-12-20 - Update .travis.yml
  * 2017-12-06 - +codecov.io
* [v0.8.2](https://github.com/jedie/django-reversion-compare/compare/v0.8.1...v0.8.2)
  * 2017-12-06 - + Minges, Alexander
  * 2017-12-06 - log exception
  * 2017-12-06 - code cleanup
  * 2017-12-06 - remove max version
  * 2017-12-06 - update README.creole to ReSt code
  * 2017-12-06 - update "./setup.py publish"
  * 2017-12-06 - Update README.creole
  * 2017-12-06 - Update __init__.py
  * 2017-12-06 - +Larin, Nikita
  * 2017-11-17 - Update .travis.yml
  * 2017-10-05 - Add possibility to count related objects as changed only if the object was replaced by another or deleted.
  * 2017-10-02 - Add some "db query count" tests, see: #95
  * 2017-10-02 - +.editorconfig
  * 2016-12-23 - work around a type error triggered by taggit
* [v0.8.1](https://github.com/jedie/django-reversion-compare/compare/v0.8.0...v0.8.1)
  * 2017-10-02 - update classifiers
  * 2017-10-02 - Update README.creole
  * 2017-10-02 - +w4rri0r3k
  * 2017-09-30 - added trans (no comment exists)
  * 2017-09-30 - Add files via upload
  * 2017-09-30 - Create django.po
  * 2017-09-29 - Fix #98
  * 2017-09-18 - work around https://github.com/travis-ci/travis-ci/issues/8363
* [v0.8.0](https://github.com/jedie/django-reversion-compare/compare/v0.7.5...v0.8.0)
  * 2017-08-17 - relase as v0.8.0
  * 2017-08-17 - try to fix: https://travis-ci.org/jedie/django-reversion-compare/builds/265579929
  * 2017-08-17 - try run tests with python 3.6
  * 2017-08-17 - activate tests with django 1.11 and drop tests with django 1.9
* [v0.7.5](https://github.com/jedie/django-reversion-compare/compare/v0.7.4...v0.7.5)
  * 2017-04-24 - +fenrrir
  * 2017-04-19 - Using the 'render' function to ensure the execution of context processors properly
* [v0.7.4](https://github.com/jedie/django-reversion-compare/compare/v0.7.3...v0.7.4)
  * 2017-04-07 - compare unicode instead of bytes on python 2
  * 2017-03-28 - Update README.creole
  * 2017-03-28 - +Puolitaival, Olli-Pekka
  * 2017-03-28 - +Tácito, Hugo
  * 2017-03-28 - Update admin.py
  * 2017-03-23 - Add Finnish localisations
* [v0.7.3](https://github.com/jedie/django-reversion-compare/compare/v0.7.2...v0.7.3)
  * 2016-12-22 - Update AUTHORS
  * 2016-12-22 - Update README.creole
  * 2016-12-22 - delete unused pieces of code
  * 2016-12-22 - add check is callable compare function
* [v0.7.2](https://github.com/jedie/django-reversion-compare/compare/v0.7.1...v0.7.2)
  * 2016-10-24 - Don't scan the .tox tree
  * 2016-10-20 - Revert "setup.py - don't package tests"
  * 2016-10-20 - add requirements-dev.txt
  * 2016-10-20 - +Chainz, Adam
  * 2016-10-07 - setup.py - don't package tests
  * 2016-10-05 - Remove @python_2_unicode_compatible from models without __str__
  * 2016-10-05 - Fix remote FK fetching on Django 1.10
  * 2016-08-29 - rename tests to reversion_compare_tests
  * 2016-08-29 - run tests with django v1.10
  * 2016-08-29 - "rebase" version number ;)
  * 2016-08-26 - WIP: changes for django v1.10
  * 2016-08-25 - Update README.creole
* [v0.7.1](https://github.com/jedie/django-reversion-compare/compare/v0.7.0...v0.7.1)
  * 2016-08-29 - rename test settings
  * 2016-08-29 - v0.7.1 is not ready for django v1.10
  * 2016-08-29 - Fix #79
* [v0.7.0](https://github.com/jedie/django-reversion-compare/compare/v0.6.3...v0.7.0)
  * 2016-08-25 - refactor google-diff-match-patch tests
  * 2016-08-25 - remove python<2.7 stuff
  * 2016-08-25 - v0.7.0
  * 2016-08-25 - +coverage report
  * 2016-08-25 - update README
  * 2016-08-25 - try to fix CI
  * 2016-08-23 - update travis
  * 2016-08-23 - +.tox +.coverage
  * 2016-08-23 - remove reversion_api and import everything directly
  * 2016-08-23 - use tox
  * 2016-08-23 - cleanup
  * 2016-08-18 - Update for django-reversion 2.0
  * 2016-06-27 - Update setup.py
  * 2016-06-14 - for PyPi ReSt
* [v0.6.3](https://github.com/jedie/django-reversion-compare/compare/v0.6.2...v0.6.3)
  * 2016-06-14 - update README - pull #69
  * 2016-06-13 - README - remove forum link
  * 2016-05-23 - Remove unused and deprecated `patters`
  * 2016-04-28 - Update README.creole
  * 2016-04-28 - +pypetey
  * 2016-04-17 - Update admin.py
* [v0.6.2](https://github.com/jedie/django-reversion-compare/compare/v0.6.1...v0.6.2)
  * 2016-04-27 - add LICENSE, fix for #68
  * 2016-03-31 - Update __init__.py
  * 2016-03-31 - Update README.creole
  * 2016-03-31 - +logaritmisk +amureki
  * 2016-03-31 - Check if related model has int as pk for ManyToMany fields instead if current model.
  * 2016-03-25 - Added choices field representation
* [v0.6.1](https://github.com/jedie/django-reversion-compare/compare/v0.6.0...v0.6.1)
  * 2016-02-16 - Update pull info
  * 2016-02-16 - Fix English source text for "Field didn't exist"
  * 2016-01-13 - Fix Python error when ManyToMany relations didn't exist.
* [v0.6.0](https://github.com/jedie/django-reversion-compare/compare/v0.5.6...v0.6.0)
  * 2016-02-03 - release v0.6.0
  * 2016-02-03 - Update setup.py
  * 2016-02-03 - Update README.creole
  * 2016-02-02 - code review updates
  * 2016-02-02 - fixed hassattr, fixed py3 issue
  * 2016-02-02 - diff-match-patch
  * 2016-02-02 - import all reversion objects through a central api module
  * 2016-02-01 - revert
  * 2016-02-01 - test import fix?
  * 2016-02-01 - fixed test data
  * 2016-02-02 - Fix travis matrix
  * 2016-02-01 - clean for py2, now to fix py3
  * 2016-02-01 - added tests for #58
  * 2016-02-01 - add tests for #57, changes text
  * 2016-02-01 - small whitespace tweaks and comments, fixes #58
  * 2016-02-01 - fixes #57 when using google-diff
  * 2016-02-01 - add non-abstract parent comparisons
  * 2015-12-26 - fixed #52
  * 2016-02-01 - fix unitests for Bool fields
  * 2016-02-01 - remove deprecated warning
  * 2016-02-01 - compare_BooleanField.html
  * 2016-02-01 - update
  * 2016-02-01 - run tests with django 1.8 and 1.9
  * 2015-12-19 - Fix tests for django-reversion 0.10.x
  * 2015-12-19 - Works with Django 1.9 and django-reversion 1.10.0.
  * 2015-11-11 - +Sae X
  * 2015-11-11 - Added Dutch translation
  * 2015-11-11 - small changes for readability
  * 2015-09-23 - + Cornehl, Denis
* [v0.5.6](https://github.com/jedie/django-reversion-compare/compare/v0.5.5...v0.5.6)
  * 2015-09-23 - Another small change to README
  * 2015-09-23 - Add greek translation
  * 2015-09-23 - Add missing logger(debug) on compare module and...
  * 2015-09-22 - Another small creole syntax fix
  * 2015-09-22 - Small fixes in creole syntax
  * 2015-09-22 - Small fixes for python 3 compatibility
  * 2015-09-21 - Admin history/view for non-admin views (issue #46)
  * 2015-08-28 - Bugfix
  * 2015-08-11 - update
  * 2015-08-04 - fixes broken compare links when l10n is active
* [v0.5.5](https://github.com/jedie/django-reversion-compare/compare/v0.5.4...v0.5.5)
  * 2015-07-24 - Release fix for #41 as v0.5.5
  * 2015-07-24 - some missing translate marks
  * 2015-07-23 - Fix #41
  * 2015-07-23 - fixup! add test for broken code, will result in:
  * 2015-07-23 - WIP: add test for broken code, will result in:
  * 2015-07-23 - Speeding up the tests, see:
  * 2015-07-23 - better "run_testserver" solution
* [v0.5.4](https://github.com/jedie/django-reversion-compare/compare/v0.5.3...v0.5.4)
  * 2015-07-22 - update setup.py
  * 2015-07-22 - add compare links
  * 2015-07-22 - Add Frank to AUTHORS
  * 2015-06-18 - Remove commented line
  * 2015-06-18 - Fetch OneToOne field foreign_key from the objects attribute instead of all()
  * 2015-06-18 - Add OneToOne field test by adding/testing a Identity model
* [v0.5.3](https://github.com/jedie/django-reversion-compare/compare/v0.5.2...v0.5.3)
  * 2015-07-13 - update setup.py from:
  * 2015-07-13 - change setup.py and release as 0.5.3
  * 2015-07-02 - +donation
  * 2015-06-18 - Update README.creole
  * 2015-06-17 - add me to the authors
  * 2015-06-17 - fix RemovedInDjango19Warning
  * 2015-06-17 - remove unused QueryLogMiddleware:
  * 2015-05-20 - +Requirements Status on requires.io
  * 2015-05-06 - Update Django required version
  * 2015-04-14 - update Version compatibility
* [v0.5.2](https://github.com/jedie/django-reversion-compare/compare/v0.5.1...v0.5.2)
  * 2015-04-14 - upload as wheels, too.
  * 2015-04-11 - add django 1.8 to test suite
  * 2015-04-11 - unindenting cause I was wrong
  * 2015-04-11 - Shows only true missing objects, fixes #34
  * 2015-04-11 - django1.8 fixes, closes #33
  * 2015-02-28 - add simple script to start testserver
  * 2015-02-28 - Skip the first, unused migration run
  * 2015-02-28 - Add more unittest with VariantModel
  * 2015-02-28 - reformat code
  * 2015-02-28 - WIP: cleanup
  * 2015-02-28 - move deleted items up
  * 2015-02-28 - removed debug print statement
  * 2015-02-28 - unit tests for reverse relations
  * 2015-02-28 - first test tests for reverse
* [v0.5.1](https://github.com/jedie/django-reversion-compare/compare/v0.5.0...v0.5.1)
  * 2015-02-28 - activate previous/next links and add unitests for them
* [v0.5.0](https://github.com/jedie/django-reversion-compare/compare/v0.4.0...v0.5.0)
  * 2015-02-27 - gitignore
  * 2015-02-27 - Py2 fixes
  * 2015-02-27 - fixup! update meta
  * 2015-02-27 - update meta
  * 2015-02-27 - Bugfix: TypeError
  * 2015-02-27 - bugfix warning
  * 2015-02-27 - add docstrings
  * 2015-02-27 - WIP: refactor unitests
  * 2015-02-27 - WIP: fix wrong merge...
  * 2015-02-26 - rewrote test manage.py in 'the new way'
  * 2015-02-26 - adding to authors :)
  * 2015-02-02 - add "skip_non_revision" argument to patch_admin()
  * 2015-01-15 - added reverse foreign key
  * 2015-01-14 - add related_name for reverse relations
* [v0.4.0](https://github.com/jedie/django-reversion-compare/compare/aef6c6e...v0.4.0)
  * 2015-01-31 - Add "settings.ADD_REVERSION_ADMIN" and update README
  * 2015-01-31 - Bugfix: Add missing urlencode import
  * 2015-01-31 - force_unicode -> force_text
  * 2015-01-31 - remove obsolete imports
  * 2014-10-02 - "Django>=1.5,<1.8"
  * 2014-10-02 - WIP: Just add __future__ import
  * 2014-10-02 - WIP: Just run 2to3
  * 2014-10-02 - update setup.py
  * 2013-11-18 - update install_requires
  * 2013-11-18 - VERSION_TYPE_CHOICES was removed?
  * 2013-11-12 - Update README.creole
  * 2013-07-19 - start updates for django 1.5: change url syntax
  * 2014-08-08 - Added functional previous and next buttons on compare view
  * 2014-08-05 - added french translation
  * 2014-01-18 - handle a removed field rather than crashing
  * 2014-01-18 - drop django 1.4
  * 2014-01-18 - Django 1.6 and Reversions 1.8 compat
  * 2014-01-18 - Version Bumps all around
  * 2014-01-18 - django.conf.urls.defaults deprecated in Django 1.6
  * 2013-11-20 - Actually return fall-back field stringification
  * 2013-07-05 - Update compare.html
  * 2013-03-22 - update README
  * 2013-03-22 - Add pahaz author
  * 2013-03-22 - delete unused import
  * 2013-03-21 - Fix issues#13 (add `patch_admin` function)
  * 2013-02-15 - add more flexible context for template.
  * 2013-01-03 - Remove date from version string
  * 2012-08-31 - add contact info
  * 2012-06-20 - Fix logging error statements.
  * 2012-06-19 - Reverse admin urls in tests rather than hardcoding.
  * 2012-06-19 - Additional tests for model with non-default reversion manager.
  * 2012-06-19 - Add new test model and register in the admin with custom reversion manager. Fix test case counting registered models.
  * 2012-06-12 - Use VersionAdmin.revision_manager rather than default_revision_manager.
  * 2012-06-12 - add "django-tools" and "south" to tests_require. Thx mlavin! see also: https://github.com/jedie/django-reversion-compare/commit/3e62a4a1276cd5a7330b88211d675282634a84b2
  * 2012-06-12 - South not directly needed, see: https://github.com/jedie/django-reversion-compare/commit/3e62a4a1276cd5a7330b88211d675282634a84b2#commitcomment-1449100
  * 2012-06-11 - south also needed
  * 2012-06-11 - Add tests for TextField
  * 2012-06-11 - bugfix for python 2.6
  * 2012-06-11 - add a model with all variants of all existing types. TODO: add unittests for all variants!
  * 2012-06-05 - add link/image to Travis CI
  * 2012-06-05 - django-tools needed for tests
  * 2012-06-05 - django-reversion needed south
  * 2012-06-05 - Add Travis CI configuration file
  * 2012-06-04 - fix links to screenshots
  * 2012-06-04 - run test with "./setup.py test"
  * 2012-06-04 - a little bit faster
  * 2012-06-04 - add work-a-round for https://github.com/jedie/django-reversion-compare/issues/5
  * 2012-06-04 - Update master
  * 2012-06-01 - don't use hardcoded version IDs in tests
  * 2012-06-01 - add info that django-tools used in unittests
  * 2012-06-01 - add bmihelac
  * 2012-06-01 - Note that min django version is 1.4
  * 2012-06-01 - FIX: Do not use print
  * 2012-06-01 - FIX: null type error
  * 2012-05-18 - use unified_diff for bigger text blocks.
  * 2012-05-16 - Enhanced handling of m2m changes with follow and non-follow relations.
  * 2012-05-16 - bugfix in html code: it's not a header ;)
  * 2012-05-15 - add form error in debug mode
  * 2012-05-15 - variant 2 is better, because reversion.get_for_object() will filter by obj.__class__, too and not only by obj.pk! So you will get strage errors, if version ID doesn't be a version from the same object! see also: https://github.com/jedie/django-reversion-compare/commit/9c8bd85ea263de3da1b7441e35061ac97f7df1de#L0L382
  * 2012-05-15 - compare m2m in the right way. Add unittests for them, too.
  * 2012-05-15 - good idea to see the "type", too.
  * 2012-05-15 - wrong template
  * 2012-05-14 - add backwards and forwards links in history view see also: https://github.com/etianen/django-reversion/issues/155
  * 2012-05-14 - * cleanup models/admin: Implement only models for unittests.
  * 2012-05-14 - * run all tests without google-diff-match-patch as default * some tests can activate it temporary
  * 2012-05-14 - all empty models.py for unittests
  * 2012-05-10 - update running unittests
  * 2012-05-10 - First useful unittests!
  * 2012-05-10 - start implementing unittest, but current code is broken ;)
  * 2012-05-10 - add variant and broken code
  * 2012-05-10 - found a very simple way without the need to hack the related manager: Simply get a "fresh" model manager. See also: https://github.com/etianen/django-reversion/issues/153#issuecomment-5620757
  * 2012-05-09 - Bugfix: check m2m only if the current field is a m2m
  * 2012-05-09 - Fix for ReSt formatting (<string>:102: (ERROR/3) Document or section may not begin with a transition.)
  * 2012-05-09 - Add a many-to-many compare item-by-item
  * 2012-05-09 - "enlarge" style match
  * 2012-05-09 - add a work-a-round to get all m2m objects, see: https://github.com/etianen/django-reversion/issues/153
  * 2012-05-09 - better to_string() results
  * 2012-05-09 - add example models for many-to-many compare
  * 2012-05-09 - Add compare of many-to-many fields
  * 2012-05-09 - make ForeignKey(User) optional
  * 2012-05-09 - Add admin classes for django-reversion models, too.
  * 2012-05-09 - cleanup
  * 2012-05-09 - more info in debug()
  * 2012-05-08 - mark paragraphs in google-diff-match-patch are IMHO needlessly
  * 2012-05-08 - remove patch_admin(), it's in django-reversion.
  * 2012-05-08 - misspelled
  * 2012-05-08 - add info about google-diff-match-patch
  * 2012-05-08 - bugfix: this should only be used for developing ;)
  * 2012-05-08 - ignore .settings
  * 2012-05-08 - add django, django-reversion as requires in setup.py
  * 2012-05-08 - chmod +x
  * 2012-05-08 - more examples
  * 2012-05-08 - README, LICENSE...
  * 2012-05-08 - change README
  * 2012-05-08 - change screenshots
  * 2012-05-08 - Use field.verbose_name and display field.help_text if exists
  * 2012-05-08 - Use a generic add/remove. Now only for ForeignKey and FileField
  * 2012-05-08 - change debug
  * 2012-05-08 - display revision comment.
  * 2012-05-08 - Add genereic ForeignKey compare.
  * 2012-05-08 - remove date time overwrite
  * 2012-05-08 - add info how to test
  * 2012-05-08 - Split BaseCompareVersionAdmin and CompareVersionAdmin: CompareVersionAdmin should store predefined compare methods.
  * 2012-05-08 - use <del> and <ins> instead of "span class"
  * 2012-05-08 - add default username/email
  * 2012-05-08 - rename test app
  * 2012-05-08 - first usable stage
  * 2012-05-08 - setup test project
  * 2012-05-08 - add project
  * 2012-05-08 - update MANIFEST, gitignore
  * 2012-05-08 - change homepage
  * 2012-05-08 - undelete the test_project
  * 2012-05-08 - start collecting all needed code for begining a seperat project.
  * 2012-05-07 - Add two ways to define own compage methods: "compare_%s" % field_name or "compare_%s" % field.get_internal_type()
  * 2012-05-07 - better docstring
  * 2012-05-07 - cleanup the helper stuff and remove pygments: Use google-diff-match-patch if installed. Fallback: ndiff with a simple highlight.
  * 2012-05-07 - * moved the compare stuff from VersionAdmin into CompareVersionAdmin * Add compare_fields and compare_exclude * Make it more flexible: Admin class can define own methods for every field to compare the difference
  * 2012-05-07 - changed TABs to spaces
  * 2012-05-07 - TABs to spaces
  * 2012-05-07 - * The compare view can be disabled/enabled by set compare to None or to a callable object. * Insert compare submit button only, if there are at least two versions
  * 2012-05-07 - move the "make compare" stuff into helpers.
  * 2012-05-07 - Compare always the newest one with the older one
  * 2012-05-07 - change the compare method to a per-field-diff
  * 2012-05-07 - * rename "diff" to "compare"
  * 2012-05-07 - pre selecting the compare radio buttons depend on history_latest_first, see also: https://github.com/etianen/django-reversion/issues/77
  * 2012-05-03 - Returning the created revision from save_revision()
  * 2012-05-03 - Bugfix: Missing renaming from https://github.com/etianen/django-reversion/commit/b32e08ab23c20c6219ef91018db4b8b0d24e29b9
  * 2012-05-03 - corrent new/old
  * 2012-05-03 - removed unused code.
  * 2012-05-03 - add generic html diff view.
  * 2012-04-30 - Removing mixin admin separation.
  * 2012-04-30 - Creating mixin classes for the reversion admin integration.
  * 2012-03-29 - Fixing potential issue with south migration 0004.
  * 2012-03-27 - Updating changelog for 1.6 release.
  * 2012-03-27 - Fixing download URL.
  * 2012-03-27 - Bumping version number
  * 2012-03-27 - Fixing version number in source.
  * 2012-03-27 - Updating for 1.5.2 release.
  * 2012-03-11 - Added in new pre_revision_commit and post_revision_commit signals. This is the start of the implementation of #139.
  * 2012-03-09 - Fixing saving version data with M2M relationships. Fixes #138
  * 2012-03-08 - Adding in hook for composing revision instances.
  * 2012-03-07 - Cleaning up unused import.
  * 2012-03-07 - Removing ambiguity with admin revision context manager.
  * 2012-03-07 - Stopping registration of auth.User from breaking tests. Fixes #125 and #126.
  * 2012-03-07 - Using sqlite for testing.
  * 2012-03-07 - Adding in hack for MySQL server bug in get_deleted view. Fixes #118
  * 2012-03-06 - Using a partial function to scope formset hack.
  * 2012-03-06 - Allowing version meta admin to work with non-int-pk models.
  * 2012-03-06 - Using manage_manually in reversion admin to avoid django database transaction nightmare.
  * 2012-03-06 - Adding in manage_manually option for revision management.
  * 2012-03-03 - Corrected file django-reversion/src/reversion/locale/pt_BR/LC_MESSAGES/django.po
  * 2012-03-02 - Added locale for pt_BR (Brazilian Portuguese)
  * 2012-02-29 - Removing outdated blog link.
  * 2012-02-15 - Adding in fix for issue #128 - tests (CreateInitialRevisionsTest and VersionAdminTest) failing
  * 2012-02-10 - Possible fix for #104
  * 2012-02-09 - Fixing error in parent revision recovery.
  * 2012-02-05 - Separing out do_revert into a separate helper function called safe_revert. Fixes #83.
  * 2012-02-04 - Decoupling model db and reversion db in get_deleted method
  * 2012-02-03 - Refactoring multi-db support to use set_db and get_db methods.
  * 2012-01-31 - Quote/unquote admin urls
  * 2012-01-31 - Throwing RegistrationError if VersionAdmin is used with a proxy model.
  * 2012-01-30 - Allow object pks to have slashes in them
  * 2011-12-17 - Added in experimental VersionMetaAdmin class.
  * 2011-12-07 - Sending a list of fields to serialize when serializing models.
  * 2011-12-07 - Fixing pull request #116
  * 2011-12-07 - Fixed issue 110 (testCreateInitialRevisions fails for models with initial_data)
  * 2011-11-21 - Fix 78411523 to work with Python 2.5 which doesn't know about class decorators (PEP 3129)
  * 2011-11-18 - Skip test on admin integration if django.contrib.admin is not activated
  * 2011-11-14 - Found a way around peeking into the model state for multi-db support. yay!
  * 2011-11-14 - Made modifications to multi-db support to be a bit more consistent throughout the API to encourage use of the 'db' through out instead of depending on the model private state. Although there are two exceptions to this when using signals, since we don't control how our API gets called here.
  * 2011-11-13 - Adding support for multiple db
  * 2011-11-10 - Allow non-ASCII text in diffs.
  * 2011-11-09 - Increment supported Django version for django-1.4 branch
  * 2011-11-07 - InlineAdminFormSet has a different `__init__` in Django 1.4
  * 2011-11-04 - Fixed reversion admin for django 1.4
  * 2011-10-28 - Do not follow hidden foreign keys
  * 2011-10-26 - Updating setup.py version number.
  * 2011-10-26 - Updating for 1.5.1 release.
  * 2011-10-26 - Fixing #41 VersionAdmin.__init__ does not handle inline models with a OneToOneField
  * 2011-10-26 - Fixed #95: RegistrationError with GenericRelation
  * 2011-10-26 - Removed error if request finishes with open revision.
  * 2011-10-26 - Fixing random formatting errors, and unused imports.
  * 2011-10-24 - Check for GenericInlineModelAdmin first, so it gets picked up
  * 2011-10-24 - Remove ipdb
  * 2011-10-24 - Import InlineModelAdmin from the right place
  * 2011-10-24 - check for InlineModelAdmin subclasses rather than TabularInline and StackedInline
  * 2011-10-17 - Fix django version warning with multiple versions
  * 2011-10-17 - fixed typo in RevisionManage._pre_delete_receiver docstring
  * 2011-10-17 - Added norwegian translation.
  * 2011-10-13 - Enabling one-to-one fields to be used with the indexed speedups
  * 2011-10-07 - Added in tests for fix to recover list generation.
  * 2011-10-07 - Fixing error in recovering deleted revisions.
  * 2011-09-28 - Updated the french translation.
  * 2011-09-28 - Fixed translation in recover_form template to be coherent with other templates.
  * 2011-09-28 - Revert f5ddc21ac16f990b383993b555957b6779409d5d^..HEAD
  * 2011-09-21 - Updated the french translation for the last 2 fixes (removing plural form and fixing parenthesis)
  * 2011-09-21 - Removed plural form of model/object for "Recover deleted obj".
  * 2011-09-21 - Fixed the closing parenthesis of the "Deleted model" comment (gettext translation).
  * 2011-09-15 - Added in fix for Python2.5 test compatibility.
  * 2011-09-15 - Namespacing test models to avoid naming collisions with other apps.
  * 2011-09-13 - Fixed translation access of DATETIME_FORMAT in change message in admin.
  * 2011-09-11 - Added in support for multiple allowed versions of Django
  * 2011-09-09 - Tweaking for python 2.4 compatibility.
  * 2011-09-08 - Added in test for error with deleted versions being recreated.
  * 2011-09-08 - Fixing error with deleted versions being recreated.
  * 2011-09-07 - Updated version umber and download URL.
  * 2011-09-04 - Making tests compatible with Python 2.5
  * 2011-09-04 - Updating readme for wiki updates.
  * 2011-09-04 - Updated changelog for 1.5 release.
  * 2011-09-04 - Added in history_latest_first parameter on VersionAdmin. Fixes https://github.com/etianen/django-reversion/issues/77
  * 2011-09-04 - Added in more admin hacks to make revert work with inline files.
  * 2011-09-04 - Added in admin hacks that seem to fix related file issues.
  * 2011-09-04 - Added in support for nested RevisionMiddleware. Just in case that randomly happens.
  * 2011-09-04 - Updating admin integration to use new reversion API
  * 2011-09-04 - Added in warning if incorrect version of Django is detected.
  * 2011-09-04 - Fixing typo in doctests.
  * 2011-09-04 - Added in tests for complete admin created / update / revert / recover lifecycle.
  * 2011-09-04 - Added in some tests for VersionAdmin
  * 2011-09-04 - Added in test for revert delete with a delete flag in the revision.
  * 2011-09-04 - Updating doc comments with deprecation notices.
  * 2011-09-04 - Making the create_revision decorator also work as a context manager.
  * 2011-09-02 - Minor docstring corrections.
  * 2011-09-02 - Fixing spelling error.
  * 2011-09-02 - Added in tests for fields and exclude registration params.
  * 2011-09-02 - Refactored patch tests
  * 2011-09-02 - Added in tests for ignoring duplicates.
  * 2011-09-02 - Added in tests for meta.
  * 2011-09-02 - Added in tests for multi table inheritance.
  * 2011-09-02 - Updated tests to disallow proxy models. They're fundamentally broken with django-reversion.
  * 2011-09-02 - Added in tests for proxy model API useage.
  * 2011-09-02 - Added in tests for proxy model registration
  * 2011-09-02 - Added in test for one-to-many follows with revert deletes.
  * 2011-09-02 - Added in test for reverse relationship following
  * 2011-09-02 - Removed admin jsi8n hack
  * 2011-09-02 - Removed some deprecated methods from the admin.
  * 2011-09-02 - Added in more deprecation warnings.
  * 2011-09-01 - Updating TODO list.
  * 2011-09-01 - Fixing typo for deprecated.
  * 2011-09-01 - Added in test for revision revert and delete.
  * 2011-09-01 - Added in test for revision revert.
  * 2011-09-01 - Added in test for version revert.
  * 2011-09-01 - Using property decorators.
  * 2011-09-01 - Removing superfluous errors module.
  * 2011-09-01 - Added in tests for follow relationships.
  * 2011-09-01 - Added in tests for revision middleware.
  * 2011-09-01 - Added in tests for invalidated revisions.
  * 2011-09-01 - Renamed revisions.revision to revisions.default_revision_manager
  * 2011-09-01 - Added in tests for low level API useage.
  * 2011-09-01 - Moving old model manager-based api methods to revision manager.
  * 2011-09-01 - Added in warnings about pending deprications.
  * 2011-09-01 - Cleaned up test code a little.
  * 2011-09-01 - Added in tests for createinitialrevisions command.
  * 2011-09-01 - Added in tests for new registration paradigm.
  * 2011-09-01 - Adding in framework for new tests.
  * 2011-09-01 - Fixing reversion tests.
  * 2011-08-31 - Added in fixes for middleware.
  * 2011-08-31 - Reviewing tests for registration logic.
  * 2011-08-31 - Simplifying followed relations logic.
  * 2011-08-31 - Replacing a list comprehension with a generator expression.
  * 2011-08-31 - Whitespace fix.
  * 2011-08-31 - Added in slug for individual revision managers, and improved efficiency of createinitialrevisions command.
  * 2011-08-31 - Moved amputated ./manage.py file back into the test_project
  * 2011-08-31 - Renamed top-level create_on_success decorator to create_revision.
  * 2011-08-31 - Fairly large refactor of the revision management backend.
  * 2011-08-31 - Cleaning up the codebase a little.
  * 2011-08-26 - Removed some accidentally-included test files.
  * 2011-08-21 - Switching back to sqlite3 backend for testing.
  * 2011-08-21 - Added in fix for tests in sqlite3
  * 2011-08-21 - Seriously improving performance of Version.get_deleted() for models with integer primary keys.
  * 2011-08-21 - Added in test for ordering of loading deleted models.
  * 2011-08-21 - Fixing error in detecting integer primary key on model.
  * 2011-08-21 - Optimizing sort for deleted models.
  * 2011-08-21 - Quicker createinitialrevisions for models with string primary keys.
  * 2011-08-21 - Slightly more efficient list comprehension.
  * 2011-08-20 - Making migration 0004 clean up revisions that refere to content types that no longer exist.
  * 2011-08-20 - Added in GenericForeignKey for Version object.
  * 2011-08-20 - Correcting a minor typo in the README file.
  * 2011-08-20 - Updating README file to warn people about database migrations.
  * 2011-08-20 - Updated changelog.
  * 2011-08-20 - Updated tests to allow for code with and without speedups
  * 2011-08-20 - Adding in tests for models with string primary keys.
  * 2011-08-20 - Added in speedup for createinitialrevisions.
  * 2011-08-20 - Added in speedup for looking up all deleted objects of a given type.
  * 2011-08-20 - Added in speedup for looking up a deleted version of an object.
  * 2011-08-20 - Added in speedup for looking up versions for an object.
  * 2011-08-20 - Added in support for indexed speedups. Currently this is write-only.
  * 2011-08-20 - Added stricter checks for open revisions in the request machinery. It should be impossible, but someone could potentally break something using the low level API, and this will make it fail noisily rather than silently.
  * 2011-08-20 - Fixing issue #66: Object IDs with special characters
  * 2011-08-16 - Renaming style param to cleanup for generating diffs.
  * 2011-08-16 - Cleaning up doc strings for new style parameter in patch helpers.
  * 2011-08-15 - FIX attr value, it SHOWS an TypeError when the value is different to STR, now the value is forced to 'str' to fix it
  * 2011-08-15 - Addign support to identify "Semantic" or "Efficiency" cleanup
  * 2011-07-15 - allow to run createinitialrevisions on Models (verbose names) containing non-ascii chars
  * 2011-07-07 - Removing hyphen from missing users in object_history view.
  * 2011-06-21 - Bugfix: Username is optional in model.
  * 2011-05-25 - Putting in a hack to fix issue #55 - South Breaks Tests in test.py. The real fix needs to be done in South, as per http://south.aeracode.org/ticket/520
  * 2011-05-25 - Added in fix for issue #60 - Problems with the serialization of custom Fields
  * 2011-05-25 - Better fix for excluded file fields.
  * 2011-05-10 - Fix for excluded FileFields
  * 2011-05-06 - delete files marked as deleted when revert is called with delete=True
  * 2011-04-27 - Including readme in distribution.
  * 2011-04-27 - Updated changelog and download URL.
  * 2011-04-27 - Added in version number for 1.4 release.
  * 2011-04-25 - Removed the years and months options from deleterevisions, and corrected some human-readable feedback from the command.
  * 2011-04-25 - Fixed issue #48: Update change_list template to duplicate less code for Django 1.3
  * 2011-04-22 - Added in optional babel support. This makes reversion play nicer with Ththe Debian packaging system.
  * 2011-04-07 - A few code style change for reversion template patch. Nothing major.
  * 2011-04-01 - Give the recover/revert renderer enough context to know what it's doing. This lets users override all of change_form/revision_form/recover_form with a single template.
  * 2011-04-01 - Allow per-app and per-model overriding of some form templates. Specifically, revision_list, revision_form, and recover_form. This follows the same algorithm as Django uses for most of its admin forms.
  * 2011-03-31 - Fixed small errors in French translations.
  * 2011-03-31 - Revert commit of bad changes to translations (f3adc34889e3b7e8536f794bf15993edf6ccbfea).
  * 2011-03-29 - Removed wrapper around file fields. This is no longer required in Django 1.3
  * 2011-03-29 - Added in fix for revert delete=True functionality.
  * 2011-03-29 - Added in test for broken revert delete=True functionality.
  * 2011-03-25 - Added in corect version number
  * 2011-03-22 - Added a hasattr() check in middleware to handle the case where request has no user attribute defined.
  * 2011-03-21 - Updated Polish translation.
  * 2011-03-14 - Updating setup.py to ensure that migrations are packaged with the egg.
  * 2011-03-11 - Making admin work properly with new version type flag
  * 2011-03-11 - Whitespace tweak
  * 2011-03-11 - Fixed bug with following revisions
  * 2011-03-11 - Added in fix for issue #41 - VersionAdmin.__init__ does not handle inline models with a OneToOneField
  * 2011-03-11 - Minor foobar in the new settings.
  * 2011-03-11 - Added in migration for schema change
  * 2011-03-11 - Adding in south migrations
  * 2011-03-11 - Adding in tests to check for stat gathering
  * 2011-03-11 - Removing a sqlite file. Why was that in there anyway?
  * 2011-03-11 - Removed old manager module, to prevent cyclic imports
  * 2011-03-11 - Added in new settings and manage.py from django 1.3
  * 2011-03-11 - Provisional working version for reversion version flags
  * 2011-03-11 - First attempt at adding version type flag
  * 2011-03-05 - Updating download URL for pypi
  * 2011-03-05 - Updating version number for pypi
  * 2011-03-05 - Updating changelog for 1.3.3 release
  * 2011-02-22 - Fixed one serious typo (a minus in order_by) and small cleanups in deleterevisions command.
  * 2011-02-22 - Added the keep options. Removed unnecessary versions deletions (Django take care of it).
  * 2011-02-16 - Added in partial fix for issue #33. Still have error with not recovering files.
  * 2011-02-12 - Lots of refactoring and cleanup. Removed a loop of queries. Added no-confirmation flag and more verbose messages.
  * 2011-02-05 - Fixed date query in apps/models query.
  * 2011-02-05 - Lot of fixes, improved messages, fixed typos.
  * 2011-02-04 - Added draft version of the deleterevisons command.
  * 2011-02-02 - Cleaning up a bit of whitespace after merge.
  * 2011-01-23 - Expanding reversed urls in reversion.admin to account for AdminSite objects with alternate name attribute
  * 2011-01-21 - Tweaked new --comment option for createinitialrevision to thread through the comment option rather than store in self.
  * 2011-01-21 - Added in extra option for createinitialrevisions command.
  * 2011-01-13 - Fixed minor bug in new foreign key resolution code.
  * 2011-01-12 - Updated revert method to be a bit more persistant with regard to database integrity errors, and to report failures to the user.
  * 2011-01-12 - Added in fix for issue #15 - Error in Tests that an entire revision can be recovered with MySQL (ver. 1.3.2) https://github.com/etianen/django-reversion/issues/#issue/15
  * 2011-01-12 - Added in czech translation
  * 2011-01-04 - Changed that the options dict without the 'comment' key should raise an error.
  * 2011-01-04 - Added a '--comment' option to createinitialversion command to specify a custom comment for initial versions.
  * 2011-01-02 - Added in possible fix for posgres transaction issue
  * 2010-12-22 - Now using message 'Initial version.' for add message in VersionAdmin.
  * 2010-12-14 - Added 'Initial version.' as comment when adding a new object (updated translations also).
  * 2010-12-07 - Partial fix to issue #15 (entire revison cannot be recovered with MySQL).
  * 2010-11-30 - Fixing variable name inconsistency.
  * 2010-11-30 - Added in tests for new duplicate ignoring.
  * 2010-11-30 - Added in admin support for configuring handling of duplicate revisions
  * 2010-11-30 - Fixing broken tests with new code.
  * 2010-11-30 - Review an code style changes for merged code.
  * 2010-11-30 - Fixed bug with file fields in related admin formsets. Issue #2 is now closed. https://github.com/etianen/django-reversion/issues#issue/2
  * 2010-11-30 - Fixed the problem with reverting file fields in the admin. Finally get to close issue #1 :O https://github.com/etianen/django-reversion/issues#issue/1
  * 2010-11-30 - Added in some additional debugging information to createinitialrevisions (fixes issue #21 https://github.com/etianen/django-reversion/issues#issue/21)
  * 2010-11-30 - Fixing test project generic relations.
  * 2010-11-30 - Fixing error in admin related revert
  * 2010-11-30 - Fixed bug with requiring related modely to have id field in VersionAdmin.
  * 2010-11-29 - Optimize the detection of changes when saving a revision.
  * 2010-11-29 - Moved and adapt the test to prevent saving a new revision if there's no change into RevisionManager.end().
  * 2010-11-25 - Slight memory improvement on get_deleted()
  * 2010-11-25 - Added in fix for oracle crashing on distinct clauses with TextField. Fixes issue #22 https://github.com/etianen/django-reversion/issues#issue/22
  * 2010-11-25 - Added in fix for wierd MySQL bug. Fixes issue #18 https://github.com/etianen/django-reversion/issues/issue/18/
  * 2010-11-22 - Slightly more efficient version of the get_deleted implementation.
  * 2010-11-22 - Making the Version.objects.get_deleted() method much faster for large datasets.
  * 2010-11-08 - Fixed issue #16, UnicodeEncodeError in createinitialrevisions command when model verbose name have non-ASCII characters. https://github.com/etianen/django-reversion/issues#issue/16
  * 2010-11-08 - Correcting spelling mistake in doc comments.
  * 2010-11-05 - Temporary disabled some tests that give error with MySQL.
  * 2010-11-04 - Change sdtout.write by print in createinitialrevision command to avoid UnicodeEncodeError in certain context when the model verbose name have non-ASCII characters. Not sure it's a good fix in the long term?
  * 2010-11-02 - Added test to prevent saving a new revision if there's no change.
  * 2010-10-22 - Added in better download URL that PyPi should hopefully recognize
  * 2010-10-22 - Updated setup.py for new release
  * 2010-10-22 - Updated changelog for 1.3.2 release.
  * 2010-10-12 - Added Polish translation.
  * 2010-10-01 - Added french locale
  * 2010-09-16 - Using unicode field fallback in diff helpers.
  * 2010-09-03 - diff helpers can choke on fields with null=True since diff-match-patch expects to receive only strings, not None
  * 2010-09-16 - Tweaking setup.py to fix issue #9 http://github.com/etianen/django-reversion/issues#issue/9
  * 2010-09-15 - Added new management commands to setup.py, fixing issue #8 http://github.com/etianen/django-reversion/issues#issue/8
  * 2010-09-08 - Added in tests for custom serialization format
  * 2010-09-08 - Added in tests for restricted registration fields
  * 2010-09-08 - Added in unit tests for ManyToMany field following.
  * 2010-09-08 - Added in recover and revert tests for ForeignKey and OneToMany relationships
  * 2010-09-08 - Added in query tests for ForeignKey and OneToMany relationships
  * 2010-09-08 - Cleaning up some unused imports
  * 2010-09-08 - Added in test for model recover.
  * 2010-09-08 - Added in test for model revert.
  * 2010-09-08 - Added in unit tests for reversion deleted object queries
  * 2010-09-08 - Added in unit tests for reversion queries.
  * 2010-09-08 - Added in more unit tests.
  * 2010-09-08 - Replacing old doc tests with unit tests.
  * 2010-09-08 - Added in test model and integrated with patch tests.
  * 2010-09-08 - Made the manager.get_deleted() method more scaleable, at the expense of some performance. This also fixes sqlite max query size errors.
  * 2010-09-08 - Fixed comment
  * 2010-09-08 - Made the createinitialrevision management command more scaleable, at the expense of some performance. Now it actually works in sqlite for large model sets. Fixes issue #7 http://github.com/etianen/django-reversion/issues#issue/7
  * 2010-08-23 - Removed some unneccessary imports.
  * 2010-08-23 - Added some dependencies from old management command.
  * 2010-08-23 - Removed old post_syncdb hook, which wasn't playing nice with other 3rd party apps.
  * 2010-08-23 - Renamed new management command.
  * 2010-08-23 - Tweaked formating to fit project code style (pedantic)
  * 2010-08-14 - new management command for initial reverisons for all or specified apps
  * 2010-08-06 - Tweaking readme formatting
  * 2010-08-06 - Added in links to new project site on GitHub.
  * 2010-07-08 - Silly whitespace fix.
  * 2010-07-08 - Added markdown formatting to readme and CHANGELOG for better github integration.
  * 2010-07-08 - Added in CHANGELOG
  * 2010-07-08 - Added in fix for issue 68: DoesNotExist exception with follows and OneToOneFields
  * 2010-07-08 - Removed some Python 2.3 fallbacks.
  * 2010-05-31 - Changing version number, after fighting with Google Code.
  * 2010-05-31 - Moved metadata to project root
  * 2010-05-31 - Modified setup.py for 1.3 release
  * 2010-05-06 - Putting in the patch from issue 62 - InlineForms break revert
  * 2010-05-06 - Fixed issue 65 - VersionAdmin does not support read-only fields
  * 2010-05-06 - Updated README file to be more hip.
  * 2010-04-01 - Updated admin code to fit with Django trunk. Didn't seem to be any issues with the old stuff, but it's always good to keep in sync.
  * 2010-04-01 - Now using decorators in admin.py, as there is no need to support Python 2.3 for Django 1.2
  * 2010-03-03 - Including licence in sdist.
  * 2010-03-01 - Changed reference to model.id to model.pk.
  * 2010-02-26 - Revision middleware always closes the revision.
  * 2010-02-26 - Fixing issue 29.
  * 2010-02-26 - Adding fix for issue 59. Untested in postgres.
  * 2010-02-26 - Added workaround for importing admin modules when one app depends on another.
  * 2010-01-29 - Updated setup.py to include new management package.
  * 2010-01-29 - Bugfix on post_sycdb hook.
  * 2010-01-29 - Moved revcheck to a post_syncdb hook.
  * 2010-01-29 - Added in revcheck code from Marco <marcoberi@gmail.com>. Still needs tests and potentially moving to a post sync-db hook.
  * 2010-01-21 - Added templatetags package to setup.py.
  * 2010-01-07 - Now using JSON as default serialization format for smaller storage requirements.
  * 2010-01-06 - Removed recover deleted button from popup changelist.
  * 2009-12-21 - Fixed issue 54:	Reversion unit tests always register django.contrib.auth.models.User, even if app code has already done so.
  * 2009-12-17 - Added in a better hack for fixing the js18n relative URL.
  * 2009-12-10 - Fixed issue 52: UnicodeDecodeError in revision_view
  * 2009-12-10 - Added hebrew translation.
  * 2009-11-13 - Fixed Issue 49: Passing unsaved models to reversion using api, still creates version of the model in the db
  * 2009-11-13 - Fixed issue 48: ct_fk_field_name is always object_id. Use ct_fk_field.name instead
  * 2009-10-29 - Fixed error with wrapped add_view and change_view.
  * 2009-10-28 - Removed superfluous print statement.
  * 2009-10-28 - Using a url resolver in object_history view.
  * 2009-10-28 - Added locale files to pypy package.
  * 2009-10-16 - Added Russian translations.
  * 2009-10-11 - Updated setup.py for impending release.
  * 2009-10-06 - Better test settings.
  * 2009-10-06 - Fixed error with recovering related inline models.
  * 2009-10-06 - Switched to exclusive use of url confs in VersionAdmin and templates.
  * 2009-10-04 - Fixed error with inline data (issue 33)
  * 2009-10-04 - Corrected errors with proxy models.
  * 2009-09-29 - Added license and readme files.
  * 2009-08-30 - Added transaction rollbacks to tests to play nicely with postgres.
  * 2009-08-30 - Doctests no longer require diff_match_patch.
  * 2009-08-30 - list_editable is now supported!
  * 2009-08-30 - Added in the updated Italian translation strings.
  * 2009-07-23 - Removed Eclipse metadata
  * 2009-07-23 - Final commit before the 1.1.2 release.
  * 2009-07-16 - Modified setup.py for upcoming release.
  * 2009-07-16 - Added default serialization format property for reversion admin.
  * 2009-07-09 - Standard Django advice is to not use null=True on character data fields.
  * 2009-07-01 - Added a hook for creating the initial form data used for the recover form.
  * 2009-06-19 - Fixed issue 30: KeyError raised if related model's ForeignKey to parent has editable=False
  * 2009-05-19 - Fixed problem with proxy model registration.
  * 2009-05-08 - Fixed bug with admin image fields
  * 2009-04-10 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@193 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-29 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@192 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-29 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@191 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-29 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@190 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@160 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@159 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-17 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@158 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-08 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@157 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-03-08 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@156 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-16 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@155 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-07 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@154 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-06 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@153 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-06 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@152 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-04 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@150 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-04 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@147 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-04 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@146 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-03 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@145 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-02-02 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@144 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-01-22 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@143 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-01-21 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@142 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-01-05 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@141 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-01-05 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@139 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2009-01-05 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@138 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-12-02 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@137 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-27 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@136 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-27 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@135 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-27 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@134 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-27 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@133 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-10 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@129 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-09 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@128 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-06 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@73 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-11-04 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@62 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-10-21 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@61 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-10-19 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@60 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-10-19 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@59 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-10-06 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@58 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-10-04 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@56 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-28 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@48 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-28 - Refactored revisions for better integration with database transactions.
  * 2008-09-28 - A register method has replaced VERSION_CONTROLLED_MODELS setting.
  * 2008-09-28 - Wrapped recover_revision in a transaction.
  * 2008-09-27 - Removed dependency on generators.
  * 2008-09-27 - Removed dependency on frozenset
  * 2008-09-27 - Python 2.3 compatibility
  * 2008-09-27 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@29 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-27 - Non-admin api improved!
  * 2008-09-27 - File storage is now version controlled.
  * 2008-09-27 - Object recovery works!
  * 2008-09-27 - Revisions are now wrapped in a database transaction automatically.
  * 2008-09-26 - Revert is working in the admin.
  * 2008-09-26 - Cleaned up admin code.
  * 2008-09-26 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@22 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-26 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@21 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-26 - Inheritance now works.
  * 2008-09-26 - Revisions are now single-level.
  * 2008-09-26 - About to make revisions single level.
  * 2008-09-26 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@17 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-26 - M2M relations now handled correctly
  * 2008-09-26 - M2M works in admin, but M2M relationships are being lost due to delay in signal.
  * 2008-09-26 - Admin now shows changes to formsets.
  * 2008-09-26 - Refactored basic revision mechanism to be more efficient.
  * 2008-09-25 - Revision view works for simple fields.
  * 2008-09-25 - In the process of creating the revert admin page.
  * 2008-09-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@10 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@9 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@8 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@7 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-25 - Middleware module added.
  * 2008-09-25 - Revisions now work.
  * 2008-09-25 - Basic version save and rollback is working.
  * 2008-09-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@3 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-25 - git-svn-id: https://django-reversion.googlecode.com/svn/trunk@2 ab604574-8a94-11dd-aa62-cdabd1f4ca1e
  * 2008-09-24 - Initial directory structure.

</details>


[comment]: <> (✂✂✂ auto generated history end ✂✂✂)

## Links

| Github          | [https://github.com/jedie/django-reversion-compare](https://github.com/jedie/django-reversion-compare)   |
| Python Packages | [https://pypi.org/project/django-reversion-compare/](https://pypi.org/project/django-reversion-compare/) |

## Donation


* [paypal.me/JensDiemer](https://www.paypal.me/JensDiemer)
* [Flattr This!](https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2Fdjango-reversion-compare%2F)
* Send [Bitcoins](https://www.bitcoin.org/) to [1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F](https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F)
