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


* [HistoryCompareDetailView](https://github.com/jedie/django-reversion-compare/blob/master/django-reversion-compare/views.py)

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
~/django-reversion-compare$ ./manage.py tox
```


## Backwards-incompatible changes

### v0.16.0

We use https://github.com/jedie/manage_django_project
You must reinit your dev setup.

### v0.12.0

Google "diff-match-patch" is now mandatory and not optional.


## Version compatibility

| Reversion-Compare | django-reversion | Django             | Python                                         |
| ----------------- | ---------------- | ------------------ |------------------------------------------------|
| >=v0.16.0         | v3.0             | v3.2, v4.0, v4.1   | v3.9, v3.10, v3.11                             |
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

These are the unittests variants. See also: [/pyproject.toml](https://github.com/jedie/django-reversion-compare/blob/master/pyproject.toml)
Maybe other versions are compatible, too.

## Changelog

* *dev* [compare v0.15.0...master](https://github.com/jedie/django-reversion-compare/compare/v0.15.0...master)
  * Refactor project setup and use https://github.com/jedie/manage_django_project
  * Remove support for Django v2.2 -> Test only with Django v3.2, v4.0 and v4.1
  * Remove support for Python v3.7 and 3.9 -> Test only with Python v3.9, v3.10 and v3.11
  * TBC
* v0.15.0 - 27.01.2022 [compare v0.14.1...v0.15.0](https://github.com/jedie/django-reversion-compare/compare/v0.14.1...v0.15.0)
  * Bugfix model choice fields (e.g.: django-countries fields)
  * Update project and run tests with Django v2.2, v3.2 and v4.0
  * Remove temp file usage in test project
* v0.14.1 - 19.07.2021 [compare v0.14.0...v0.14.1](https://github.com/jedie/django-reversion-compare/compare/v0.14.0...v0.14.1)
  * Enable Diff-Match-Patch "checklines" mode for better diffs
  * Speed up Revision/Version admin
* v0.14.0 - 24.02.2021 [compare v0.13.1...v0.14.0](https://github.com/jedie/django-reversion-compare/compare/v0.13.1...v0.14.0)
  * Add work-a-round for [django-reversion #859 incompatible version data](https://github.com/etianen/django-reversion/issues/859) by fallback to a ndiff JSON compare [pull #149](https://github.com/jedie/django-reversion-compare/pull/149)
  * Fix translations
* v0.13.1 - 04.02.2021 [compare v0.13.0...v0.13.1](https://github.com/jedie/django-reversion-compare/compare/v0.13.0...v0.13.1)
  * [Multiline diff formatting improvements](https://github.com/jedie/django-reversion-compare/pull/137) contributed by dbader
  * [Fix django.conf.urls.url() is deprecated](https://github.com/jedie/django-reversion-compare/pull/141) contributed by GeyseR
  * Add demo links to `HistoryCompareDetailView` in test project
  * update github actions
* v0.13.0 - 23.12.2020 [compare v0.12.2...v0.13.0](https://github.com/jedie/django-reversion-compare/compare/v0.12.2...v0.13.0)
  * Support Django v3.1
  * Stop running test with Python 3.6 and pypy3
  * Activate django-debug-toolbar in test project
  * code style (e.g.: f-strings) and remove some warnings in test project
  * some project setup updates (e.g.: fix Python and Django version restrictions)
* v0.12.2 - 24.03.2020 [compare v0.12.1...v0.12.2](https://github.com/jedie/django-reversion-compare/compare/v0.12.1...v0.12.2)
  * [Added revert button on compare view](https://github.com/jedie/django-reversion-compare/pull/130), contributed by jjarthur
* v0.12.1 - 20.03.2020 [compare v0.12.0...v0.12.1](https://github.com/jedie/django-reversion-compare/compare/v0.12.0...v0.12.1)
  * [Bugfix: Django 3.0 compatibility by change project dependencies](https://github.com/jedie/django-reversion-compare/pull/125), contributed by maxocub
  * Test project used a "auto login test user" middleware
  * Test project rename django admin title and branding
* v0.12.0 - 12.03.2020 [compare v0.11.0...v0.12.0](https://github.com/jedie/django-reversion-compare/compare/v0.11.0...v0.12.0)
  * [google-diff-match-patch](https://github.com/google/diff-match-patch) is now mandatory!
  * Diff html code are now unified to `<pre class="highlight">...</pre>`
  * Bugfix `make run-test-server`
  * Switch between Google "diff-match-patch" and `difflib.ndiff()` by size: ndiff makes more human readable diffs with small values.
* v0.11.0 - 12.03.2020 [compare v0.10.0...v0.11.0](https://github.com/jedie/django-reversion-compare/compare/v0.10.0...v0.11.0)
  * CHANGE output of diff generated with "diff-match-patch":
    * cleanup html by implement a own html pretty function instead of `diff_match_patch.diff_prettyHtml` usage
    * The html is now simmilar to the difflib usage output and doesn't contain inline styles
  * Add "diff-match-patch" as optional dependencies in poetry config
  * Bugfix Django requirements
  * code cleanup and update tests
* v0.10.0 - 19.02.2020 [compare v0.9.1...v0.10.0](https://github.com/jedie/django-reversion-compare/compare/v0.9.1...v0.10.0)
  * less restricted dependency specification see: [issues #120](https://github.com/jedie/django-reversion-compare/issues/120)
  * run tests with latest django-reversion version (currently v3.x)
* v0.9.1 - 16.02.2020 [compare v0.9.0...v0.9.1](https://github.com/jedie/django-reversion-compare/compare/v0.9.0...v0.9.1)
  * Modernize project setup and use poetry
  * Apply pyupgrade and fix/update some f-strings
  * Update test project
* v0.9.0 - 19.01.2020 [compare v0.8.7...v0.9.0](https://github.com/jedie/django-reversion-compare/compare/v0.8.7...v0.9.0)
  * Test with Python 3.8 and Django 3.0, too.
  * Run tests via github actions, too.
  * Remove support for Python 3.5 and Django v1.11
  * [actually check if model is registered #115](https://github.com/jedie/django-reversion-compare/pull/115) contributed by willtho89
  * [Remove python2 compatibility decorators #113](https://github.com/jedie/django-reversion-compare/pull/113) contributed by jeremy-engel
  * [Show username and full name from custom user model #112](https://github.com/jedie/django-reversion-compare/pull/112) contributed by berekuk
  * [Fix django-suit NoneType is not iterable #111](https://github.com/jedie/django-reversion-compare/pull/111) contributed by creativequality
  * convert old format to f-strings via flynt
  * Code style:
    * sort imports with isort
    * apply autopep8
    * lint code in CI with flake8, isort and flynt
* v0.8.7 - 06.01.2020 [compare v0.8.6...v0.8.7](https://github.com/jedie/django-reversion-compare/compare/v0.8.6...v0.8.7)
  * Add new optional settings `REVERSION_COMPARE_IGNORE_NOT_REGISTERED`, see: [issues #103](https://github.com/jedie/django-reversion-compare/issues/103)
  * reformat code with 'black'
  * some code cleanup
* v0.8.6 - 04.01.2019 [compare v0.8.5...v0.8.6](https://github.com/jedie/django-reversion-compare/compare/v0.8.5...v0.8.6)
  * Bugfix: [Use ".pk" instead of ".id" when referring to related object.](https://github.com/jedie/django-reversion-compare/pull/110) contributed by [Peter Lisák](https://github.com/peterlisak)
  * Run tests: Skip Django v1.8 and add Python v3.7
* v0.8.5 - 13.09.2018 [compare v0.8.4...v0.8.5](https://github.com/jedie/django-reversion-compare/compare/v0.8.4...v0.8.5)
  * [speed up delete checking](https://github.com/jedie/django-reversion-compare/pull/106) contributed by [LegoStormtroopr](https://github.com/LegoStormtroopr)
* v0.8.4 - 15.03.2018 [compare v0.8.3...v0.8.4](https://github.com/jedie/django-reversion-compare/compare/v0.8.3...v0.8.4)
  * [Add Django 2.0 compatibility](https://github.com/jedie/django-reversion-compare/pull/102) contributed by [samifahed](https://github.com/samifahed)
* v0.8.3 - 21.12.2017 [compare v0.8.2...v0.8.3](https://github.com/jedie/django-reversion-compare/compare/v0.8.2...v0.8.3)
  * refactor travis/tox/pytest/coverage stuff
  * Tests can be run via `python3 setup.py tox` and/or `python3 setup.py test`
  * Test also with pypy3 on Travis CI.
* [v0.8.2 - 06.12.2017](https://github.com/jedie/django-reversion-compare/compare/v0.8.1...v0.8.2):
  * [Change ForeignKey relation compare](https://github.com/jedie/django-reversion-compare/pull/100) contributed by [alaruss](https://github.com/alaruss)
  * [Work around a type error triggered by taggit](https://github.com/jedie/django-reversion-compare/pull/86) contributed by [Athemis](https://github.com/Athemis)
  * minor code changes
* [v0.8.1 - 02.10.2017](https://github.com/jedie/django-reversion-compare/compare/v0.8.0...v0.8.1):
  * [Add added polish translation](https://github.com/jedie/django-reversion-compare/pull/99) contributed by [w4rri0r3k](https://github.com/w4rri0r3k)
  * Bugfix "Django>=1.11" in setup.py
* [v0.8.0 - 17.08.2017](https://github.com/jedie/django-reversion-compare/compare/v0.7.5...v0.8.0):
  * Run tests with Django v1.11 and drop tests with Django v1.9
* [v0.7.5 - 24.04.2017](https://github.com/jedie/django-reversion-compare/compare/v0.7.4...v0.7.5):
  * [Using the 'render' function to ensure the execution of context processors properly](https://github.com/jedie/django-reversion-compare/pull/90) contributed by [Rodrigo Pinheiro Marques de Araújo](https://github.com/fenrrir)
* [v0.7.4 - 10.04.2017](https://github.com/jedie/django-reversion-compare/compare/v0.7.3...v0.7.4):
  * Bugfix for Python 2: [compare unicode instead of bytes](https://github.com/jedie/django-reversion-compare/issues/89) contributed by [Maksim Iakovlev](https://github.com/lampslave)
  * [remove 'Django20Warning'](https://github.com/jedie/django-reversion-compare/pull/88) contributed by [Hugo Tácito](https://github.com/hugotacito)
  * [Add 'Finnish' localisations](https://github.com/jedie/django-reversion-compare/pull/87) contributed by [Olli-Pekka Puolitaival](https://github.com/OPpuolitaival)
* [v0.7.3 - 08.02.2017](https://github.com/jedie/django-reversion-compare/compare/v0.7.2...v0.7.3):
  * [Fix case when model has template field which is ForeignKey](https://github.com/jedie/django-reversion-compare/pull/85) contributed by [Lagovas](https://github.com/Lagovas)
* [v0.7.2 - 20.10.2016](https://github.com/jedie/django-reversion-compare/compare/v0.7.1...v0.7.2):
  * Add Django v1.10 support
* [v0.7.1 - 29.08.2016](https://github.com/jedie/django-reversion-compare/compare/v0.7.0...v0.7.1):
  * [Fix #79: missing import if **ADD_REVERSION_ADMIN != True**](https://github.com/jedie/django-reversion-compare/issues/79)
* [v0.7.0 - 25.08.2016](https://github.com/jedie/django-reversion-compare/compare/v0.6.3...v0.7.0):
  * [support only django-reversion >= 2.0](https://github.com/jedie/django-reversion-compare/pull/76) based on a contribution by [mshannon1123](https://github.com/jedie/django-reversion-compare/pull/73)
  * remove internal **reversion_api**
  * Use tox
* [v0.6.3 - 14.06.2016](https://github.com/jedie/django-reversion-compare/compare/v0.6.2...v0.6.3):
  * [Remove unused and deprecated patters](https://github.com/jedie/django-reversion-compare/pull/69) contributed by [codingjoe](https://github.com/codingjoe)
  * [Fix django 1.10 warning #66](https://github.com/jedie/django-reversion-compare/pull/66) contributed by [pypetey](https://github.com/pypetey)
* [v0.6.2 - 27.04.2016](https://github.com/jedie/django-reversion-compare/compare/v0.6.1...v0.6.2):
  * [Added choices field representation #63](https://github.com/jedie/django-reversion-compare/pull/63) contributed by [amureki](https://github.com/amureki)
  * [Check if related model has an integer as pk for ManyToMany fields. #64](https://github.com/jedie/django-reversion-compare/pull/64) contributed by [logaritmisk](https://github.com/logaritmisk)
* [v0.6.1 - 16.02.2016](https://github.com/jedie/django-reversion-compare/compare/v0.6.0...v0.6.1):
  * [pull #61](https://github.com/jedie/django-reversion-compare/pull/61): Fix error when ManyToMany relations didn't exist contributed by [Diederik van der Boor](https://github.com/vdboor)
* [v0.6.0 - 03.02.2016](https://github.com/jedie/django-reversion-compare/compare/v0.5.6...v0.6.0):
  * Added Dutch translation contributed by [Sae X](https://github.com/SaeX)
  * Add support for Django 1.9
  * Nicer boolean compare: [#57](https://github.com/jedie/django-reversion-compare/issues/57)
  * Fix [#58 compare followed reverse foreign relation fields that are on a non-abstract parent class](https://github.com/jedie/django-reversion-compare/issues/58) contributed by LegoStormtroopr
* [v0.5.6 - 23.09.2015](https://github.com/jedie/django-reversion-compare/compare/v0.5.5...v0.5.6):
  * NEW: Class-Based-View to create non-admin views and greek translation contributed by [Serafeim Papastefanos](https://github.com/spapas).
* [v0.5.5 - 24.07.2015](https://github.com/jedie/django-reversion-compare/compare/v0.5.4...v0.5.5):
  * UnboundLocalError ('version') when creating deleted list in get_many_to_something() [#41](https://github.com/jedie/django-reversion-compare/pull/41)
* [v0.5.4 - 22.07.2015](https://github.com/jedie/django-reversion-compare/compare/v0.5.3...v0.5.4):
  * One to one field custom related name fix [#42](https://github.com/jedie/django-reversion-compare/pull/42) (contributed by frwickst and aemdy)
* [v0.5.3 - 13.07.2015](https://github.com/jedie/django-reversion-compare/compare/v0.5.2...v0.5.3):
  * Update admin.py to avoid RemovedInDjango19Warning (contributed by luzfcb)
* [v0.5.2 - 14.04.2015](https://github.com/jedie/django-reversion-compare/compare/v0.5.1...v0.5.2):
  * contributed by Samuel Spencer:
    * Added Django 1.8 support: [pull #35](https://github.com/jedie/django-reversion-compare/pull/35)
    * list of changes for reverse fields incorrectly includes a "deletion" for the item that was added in: [issues #34](https://github.com/jedie/django-reversion-compare/issues/34)
* [v0.5.1 - 28.02.2015](https://github.com/jedie/django-reversion-compare/compare/v0.5.0...v0.5.1):
  * activate previous/next links and add unitests for them
* [v0.5.0 - 27.02.2015](https://github.com/jedie/django-reversion-compare/compare/v0.4.0...v0.5.0):
  * refactory unittests, test with Django v1.7 and Python 2.7 & 3.4
* [v0.4.0 - 02.02.2015](https://github.com/jedie/django-reversion-compare/compare/v0.3.5...v0.4.0):
  * Updates for django 1.7 support
  * Add `settings.ADD_REVERSION_ADMIN`
* v0.3.5 - 03.01.2013:
  * Remove date from version string. [issues 9](https://github.com/jedie/django-reversion-compare/issues/9)
* v0.3.4 - 20.06.2012:
  * Use VersionAdmin.revision_manager rather than default_revision_manager, contributed by Mark Lavin - see: [pull request 7](https://github.com/jedie/django-reversion-compare/pull/7)
  * Use logging for all debug prints, contributed by Bojan Mihelac - see: [pull request 8](https://github.com/jedie/django-reversion-compare/pull/8)
* v0.3.3 - 11.06.2012:
  * Bugfix "ValueError: zero length field name in format" with Python 2.6 [issues 5](https://github.com/jedie/django-reversion-compare/issues/5)
* v0.3.2 - 04.06.2012:
  * Bugfix for Python 2.6 in unified_diff(), see: [AttributeError: 'module' object has no attribute '_format_range_unified'](https://github.com/jedie/django-reversion-compare/issues/5)
* v0.3.1 - 01.06.2012:
  * Bugfix: force unicode in html diff
  * Bugfix in unittests
* v0.3.0 - 16.05.2012:
  * Enhanced handling of m2m changes with follow and non-follow relations.
* v0.2.2 - 15.05.2012:
  * Compare many-to-many in the right way.
* v0.2.1 - 10.05.2012:
  * Bugfix for models which has no m2m field: [https://github.com/jedie/django-reversion-compare/commit/c8e042945a6e78e5540b6ae27666f9b0cfc94880](https://github.com/jedie/django-reversion-compare/commit/c8e042945a6e78e5540b6ae27666f9b0cfc94880)
* v0.2.0 - 09.05.2012:
  * many-to-many compare works, too.
* v0.1.0 - 08.05.2012:
  * First release
* v0.0.1 - 08.05.2012:
  * collect all compare stuff from old "diff" branch
  * see also: [https://github.com/etianen/django-reversion/issues/147](https://github.com/etianen/django-reversion/issues/147)

## Links

| Github          | [https://github.com/jedie/django-reversion-compare](https://github.com/jedie/django-reversion-compare)   |
| Python Packages | [https://pypi.org/project/django-reversion-compare/](https://pypi.org/project/django-reversion-compare/) |

## Donation


* [paypal.me/JensDiemer](https://www.paypal.me/JensDiemer)
* [Flattr This!](https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2Fdjango-reversion-compare%2F)
* Send [Bitcoins](https://www.bitcoin.org/) to [1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F](https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F)
