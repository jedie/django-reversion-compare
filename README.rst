========================
django-reversion-compare
========================

**django-reversion-compare** is an extension to `django-reversion <https://github.com/etianen/django-reversion/>`_ that provides a history compare view to compare two versions of a model which is under reversion.

Comparing model versions is not a easy task. Maybe there are different view how this should looks like.
This project will gives you a generic way to see whats has been changed.

Many parts are customizable by overwrite methods or subclassing, see above.

+--------------------------------------+--------------------------------------------------------------------+
| |Build Status on github|             | `github.com/jedie/django-reversion-compare/actions`_               |
+--------------------------------------+--------------------------------------------------------------------+
| |Coverage Status on coveralls.io|    | `coveralls.io/r/jedie/django-reversion-compare`_                   |
+--------------------------------------+--------------------------------------------------------------------+
| |Coverage Status on codecov.io|      | `codecov.io/gh/jedie/django-reversion-compare`_                    |
+--------------------------------------+--------------------------------------------------------------------+
| |Requirements Status on requires.io| | `requires.io/github/jedie/django-reversion-compare/requirements/`_ |
+--------------------------------------+--------------------------------------------------------------------+

.. |Build Status on github| image:: https://github.com/jedie/django-reversion-compare/workflows/test/badge.svg?branch=master
.. _github.com/jedie/django-reversion-compare/actions: https://github.com/jedie/django-reversion-compare/actions
.. |Coverage Status on coveralls.io| image:: https://coveralls.io/repos/jedie/django-reversion-compare/badge.svg
.. _coveralls.io/r/jedie/django-reversion-compare: https://coveralls.io/r/jedie/django-reversion-compare
.. |Coverage Status on codecov.io| image:: https://codecov.io/gh/jedie/django-reversion-compare/branch/master/graph/badge.svg
.. _codecov.io/gh/jedie/django-reversion-compare: https://codecov.io/gh/jedie/django-reversion-compare
.. |Requirements Status on requires.io| image:: https://requires.io/github/jedie/django-reversion-compare/requirements.svg
.. _requires.io/github/jedie/django-reversion-compare/requirements/: https://requires.io/github/jedie/django-reversion-compare/requirements/

------------
Installation
------------

Just use:

::

    pip install django-reversion-compare

Setup
=====

Add **reversion_compare** to **INSTALLED_APPS** in your settings.py, e.g.:

::

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

Usage
=====

Inherit from **CompareVersionAdmin** instead of **VersionAdmin** to get the comparison feature.

admin.py e.g.:

::

    from django.contrib import admin
    from reversion_compare.admin import CompareVersionAdmin
    
    from my_app.models import ExampleModel
    
    @admin.register(ExampleModel)
    class ExampleModelAdmin(CompareVersionAdmin):
        pass

If you're using an existing third party app, then you can add patch django-reversion-compare into
its admin class by using the **reversion_compare.helpers.patch_admin()** method. For example, to add
version control to the built-in User model:

::

    from reversion_compare.helpers import patch_admin
    
    patch_admin(User)

e.g.: Add django-cms Page model:

::

    from cms.models.pagemodel import Page
    from reversion_compare.helpers import patch_admin
    
    
    # Patch django-cms Page Model to add reversion-compare functionality:
    patch_admin(Page)

Customize
=========

It's possible to change the look for every field or for a entire field type.
You must only define a methods to your admin class with this name scheme:

*  ``"compare_%s" % field_name`` 

*  ``"compare_%s" % field.get_internal_type()`` 

If there is no method with this name scheme, the ``fallback_compare()`` method will be used.

An example for specifying a compare method for a model field by name:

::

    class YourAdmin(CompareVersionAdmin):
        def compare_foo_bar(self, obj_compare):
            """ compare the foo_bar model field """
            return "%r <-> %r" % (obj_compare.value1, obj_compare.value2)

and example using **patch_admin** with custom version admin class:

::

    patch_admin(User, AdminClass=YourAdmin)

----------------
Class Based View
----------------

Beyond the Admin views, you can also create a Class Based View for displaying and comparing version
differences. This is a single class-based-view that either displays the list of versions to select
for an object or displays both the versions **and** their differences (if the versions to be compared
have been selected). This class can be used just like a normal DetailView:

More information about this can be found in DocString of:

* `https://github.com/jedie/django-reversion-compare/blob/master/reversion_compare/views.py <HistoryCompareDetailView>`_

The ``make run-test-server`` test project contains a Demo, use the links under:

::

    HistoryCompareDetailView Examples:

-----------
Screenshots
-----------

Here some screenshots of django-reversion-compare:

----

How to select the versions to compare:

|django-reversion-compare_v0_1_0-01.png|

.. |django-reversion-compare_v0_1_0-01.png| image:: https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120508_django-reversion-compare_v0_1_0-01.png

----

from **v0.1.0**: DateTimeField compare (last update), TextField compare (content) with small changes and a ForeignKey compare (child model instance was added):

|django-reversion-compare_v0_1_0-02.png|

.. |django-reversion-compare_v0_1_0-02.png| image:: https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120508_django-reversion-compare_v0_1_0-02.png

----

from **v0.1.0**: Same as above, but the are more lines changed in TextField and the ForeignKey relation was removed:

|django-reversion-compare_v0_1_0-03.png|

.. |django-reversion-compare_v0_1_0-03.png| image:: https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120508_django-reversion-compare_v0_1_0-03.png

----

Example screenshot from **v0.3.0**: a many-to-many field compare (friends, hobbies):

|django-reversion-compare_v0_3_0-01.png|

.. |django-reversion-compare_v0_3_0-01.png| image:: https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-reversion-compare/20120516_django-reversion-compare_v0_3_0-01.png

* In the first line, the m2m object has been changed.

* line 2: A m2m object was deleted

* line 3: A m2m object was removed from this entry (but not deleted)

* line 4: This m2m object has not changed

----------------------------
create developer environment
----------------------------

e.g.:

::

    # Clone project (Use your fork SSH url!):
    ~$ git clone https://github.com/jedie/django-reversion-compare.git
    ~$ cd django-reversion-compare
    ~/django-reversion-compare$ make install
    ~/django-reversion-compare$ make
    help                 List all commands
    install-poetry       install or update poetry
    install              install reversion_compare via poetry
    lint                 Run code formatters and linter
    fix-code-style       Fix code formatting
    tox-listenvs         List all tox test environments
    tox                  Run pytest via tox with all environments
    tox-py36             Run pytest via tox with *python v3.6*
    tox-py37             Run pytest via tox with *python v3.7*
    tox-py38             Run pytest via tox with *python v3.8*
    pytest               Run pytest
    update-rst-readme    update README.rst from README.reversion_compare
    publish              Release new version to PyPi
    run-test-server      Start Django dev server with the test project

Helpful for writing and debugging unittests is to run a local test server with the same data.
e.g.:

::

    ~/django-reversion-compare$ make run-test-server

**migration** will be run.

Call manage commands from test project, e.g.:

::

    ~/django-reversion-compare$ poetry shell
    django-reversion-compare-foobar-py3.6) ~/django-reversion-compare$ ./reversion_compare_tests/manage.py --help
    ...

------------------------------
Backwards-incompatible changes
------------------------------

v0.12.0
=======

Google "diff-match-patch" is now mandatory and not optional.

---------------------
Version compatibility
---------------------

+-------------------+------------------+--------------------+------------------------------------------------+
| Reversion-Compare | django-reversion | Django             | Python                                         |
+===================+==================+====================+================================================+
| >=v0.13.0         | v3.0             | v2.2, v3.0, v3.1   | v3.7, v3.8, v3.9                               |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.10.0         | v3.0             | v2.2, v3.0         | v3.6, v3.7, v3.8, pypy3                        |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.9.0          | v2.0             | v2.2, v3.0         | v3.6, v3.7, v3.8, pypy3                        |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.8.6          | v2.0             | v1.11, v2.0        | v3.5, v3.6, v3.7, pypy3                        |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.8.4          | v2.0             | v1.8, v1.11, v2.0  | v3.5, v3.6, pypy3                              |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.8.3          | v2.0             | v1.8, v1.11        | v3.5, v3.6, pypy3                              |
+-------------------+------------------+--------------------+------------------------------------------------+
| v0.8.x            | v2.0             | v1.8, v1.10, v1.11 | v2.7, v3.4, v3.5, v3.6 (only with Django 1.11) |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.7.2          | v2.0             | v1.8, v1.9, v1.10  | v2.7, v3.4, v3.5                               |
+-------------------+------------------+--------------------+------------------------------------------------+
| v0.7.x            | v2.0             | v1.8, v1.9         | v2.7, v3.4, v3.5                               |
+-------------------+------------------+--------------------+------------------------------------------------+
| v0.6.x            | v1.9, v1.10      | v1.8, v1.9         | v2.7, v3.4, v3.5                               |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.5.2          | v1.9             | v1.7, v1.8         | v2.7, v3.4                                     |
+-------------------+------------------+--------------------+------------------------------------------------+
| >=v0.4            | v1.8             | v1.7               | v2.7, v3.4                                     |
+-------------------+------------------+--------------------+------------------------------------------------+
| <v0.4             | v1.6             | v1.4               | v2.7                                           |
+-------------------+------------------+--------------------+------------------------------------------------+

These are the unittests variants. See also: `/pyproject.toml <https://github.com/jedie/django-reversion-compare/blob/master/pyproject.toml>`_
Maybe other versions are compatible, too.

---------
Changelog
---------

* *dev* `compare v0.13.1...master <https://github.com/jedie/django-reversion-compare/compare/v0.13.1...master>`_ 

    * TBC

* v0.13.1 - 04.02.2021 `compare v0.13.0...v0.13.1 <https://github.com/jedie/django-reversion-compare/compare/v0.13.0...v0.13.1>`_ 

    * `Multiline diff formatting improvements <https://github.com/jedie/django-reversion-compare/pull/137>`_ contributed by dbader

    * `Fix django.conf.urls.url() is deprecated <https://github.com/jedie/django-reversion-compare/pull/141>`_ contributed by GeyseR

    * Add demo links to ``HistoryCompareDetailView`` in test project

    * update github actions

* v0.13.0 - 23.12.2020 `compare v0.12.2...v0.13.0 <https://github.com/jedie/django-reversion-compare/compare/v0.12.2...v0.13.0>`_ 

    * Support Django v3.1

    * Stop running test with Python 3.6 and pypy3

    * Activate django-debug-toolbar in test project

    * code style (e.g.: f-strings) and remove some warnings in test project

    * some project setup updates (e.g.: fix Python and Django version restrictions)

* v0.12.2 - 24.03.2020 `compare v0.12.1...v0.12.2 <https://github.com/jedie/django-reversion-compare/compare/v0.12.1...v0.12.2>`_ 

    * `Added revert button on compare view <https://github.com/jedie/django-reversion-compare/pull/130>`_, contributed by jjarthur

* v0.12.1 - 20.03.2020 `compare v0.12.0...v0.12.1 <https://github.com/jedie/django-reversion-compare/compare/v0.12.0...v0.12.1>`_ 

    * `Bugfix: Django 3.0 compatibility by change project dependencies <https://github.com/jedie/django-reversion-compare/pull/125>`_, contributed by maxocub

    * Test project used a "auto login test user" middleware

    * Test project rename django admin title and branding

* v0.12.0 - 12.03.2020 `compare v0.11.0...v0.12.0 <https://github.com/jedie/django-reversion-compare/compare/v0.11.0...v0.12.0>`_ 

    * `google-diff-match-patch <https://github.com/google/diff-match-patch>`_ is now mandatory!

    * Diff html code are now unified to ``<pre class="highlight">...</pre>``

    * Bugfix ``make run-test-server``

    * Switch between Google "diff-match-patch" and ``difflib.ndiff()`` by size: ndiff makes more human readable diffs with small values.

* v0.11.0 - 12.03.2020 `compare v0.10.0...v0.11.0 <https://github.com/jedie/django-reversion-compare/compare/v0.10.0...v0.11.0>`_ 

    * CHANGE output of diff generated with "diff-match-patch":

        * cleanup html by implement a own html pretty function instead of ``diff_match_patch.diff_prettyHtml`` usage

        * The html is now simmilar to the difflib usage output and doesn't contain inline styles

    * Add "diff-match-patch" as optional dependencies in poetry config

    * Bugfix Django requirements

    * code cleanup and update tests

* v0.10.0 - 19.02.2020 `compare v0.9.1...v0.10.0 <https://github.com/jedie/django-reversion-compare/compare/v0.9.1...v0.10.0>`_ 

    * less restricted dependency specification see: `issues #120 <https://github.com/jedie/django-reversion-compare/issues/120>`_

    * run tests with latest django-reversion version (currently v3.x)

* v0.9.1 - 16.02.2020 `compare v0.9.0...v0.9.1 <https://github.com/jedie/django-reversion-compare/compare/v0.9.0...v0.9.1>`_ 

    * Modernize project setup and use poetry

    * Apply pyupgrade and fix/update some f-strings

    * Update test project

* v0.9.0 - 19.01.2020 `compare v0.8.7...v0.9.0 <https://github.com/jedie/django-reversion-compare/compare/v0.8.7...v0.9.0>`_ 

    * Test with Python 3.8 and Django 3.0, too.

    * Run tests via github actions, too.

    * Remove support for Python 3.5 and Django v1.11

    * `actually check if model is registered #115 <https://github.com/jedie/django-reversion-compare/pull/115>`_ contributed by willtho89

    * `Remove python2 compatibility decorators #113 <https://github.com/jedie/django-reversion-compare/pull/113>`_ contributed by jeremy-engel

    * `Show username and full name from custom user model #112 <https://github.com/jedie/django-reversion-compare/pull/112>`_ contributed by berekuk

    * `Fix django-suit NoneType is not iterable #111 <https://github.com/jedie/django-reversion-compare/pull/111>`_ contributed by creativequality

    * convert old format to f-strings via flynt

    * Code style:

        * sort imports with isort

        * apply autopep8

        * lint code in CI with flake8, isort and flynt

* v0.8.7 - 06.01.2020 `compare v0.8.6...v0.8.7 <https://github.com/jedie/django-reversion-compare/compare/v0.8.6...v0.8.7>`_ 

    * Add new optional settings ``REVERSION_COMPARE_IGNORE_NOT_REGISTERED``, see: `issues #103 <https://github.com/jedie/django-reversion-compare/issues/103>`_

    * reformat code with 'black'

    * some code cleanup

* v0.8.6 - 04.01.2019 `compare v0.8.5...v0.8.6 <https://github.com/jedie/django-reversion-compare/compare/v0.8.5...v0.8.6>`_ 

    * Bugfix: `Use ".pk" instead of ".id" when referring to related object. <https://github.com/jedie/django-reversion-compare/pull/110>`_ contributed by `Peter Lisák <https://github.com/peterlisak>`_

    * Run tests: Skip Django v1.8 and add Python v3.7

* v0.8.5 - 13.09.2018 `compare v0.8.4...v0.8.5 <https://github.com/jedie/django-reversion-compare/compare/v0.8.4...v0.8.5>`_ 

    * `speed up delete checking <https://github.com/jedie/django-reversion-compare/pull/106>`_ contributed by `LegoStormtroopr <https://github.com/LegoStormtroopr>`_

* v0.8.4 - 15.03.2018 `compare v0.8.3...v0.8.4 <https://github.com/jedie/django-reversion-compare/compare/v0.8.3...v0.8.4>`_ 

    * `Add Django 2.0 compatibility <https://github.com/jedie/django-reversion-compare/pull/102>`_ contributed by `samifahed <https://github.com/samifahed>`_

* v0.8.3 - 21.12.2017 `compare v0.8.2...v0.8.3 <https://github.com/jedie/django-reversion-compare/compare/v0.8.2...v0.8.3>`_ 

    * refactor travis/tox/pytest/coverage stuff

    * Tests can be run via ``python3 setup.py tox`` and/or ``python3 setup.py test``

    * Test also with pypy3 on Travis CI.

* `v0.8.2 - 06.12.2017 <https://github.com/jedie/django-reversion-compare/compare/v0.8.1...v0.8.2>`_:

    * `Change ForeignKey relation compare <https://github.com/jedie/django-reversion-compare/pull/100>`_ contributed by `alaruss <https://github.com/alaruss>`_

    * `Work around a type error triggered by taggit <https://github.com/jedie/django-reversion-compare/pull/86>`_ contributed by `Athemis <https://github.com/Athemis>`_

    * minor code changes

* `v0.8.1 - 02.10.2017 <https://github.com/jedie/django-reversion-compare/compare/v0.8.0...v0.8.1>`_:

    * `Add added polish translation <https://github.com/jedie/django-reversion-compare/pull/99>`_ contributed by `w4rri0r3k <https://github.com/w4rri0r3k>`_

    * Bugfix "Django>=1.11" in setup.py

* `v0.8.0 - 17.08.2017 <https://github.com/jedie/django-reversion-compare/compare/v0.7.5...v0.8.0>`_:

    * Run tests with Django v1.11 and drop tests with Django v1.9

* `v0.7.5 - 24.04.2017 <https://github.com/jedie/django-reversion-compare/compare/v0.7.4...v0.7.5>`_:

    * `Using the 'render' function to ensure the execution of context processors properly <https://github.com/jedie/django-reversion-compare/pull/90>`_ contributed by `Rodrigo Pinheiro Marques de Araújo <https://github.com/fenrrir>`_

* `v0.7.4 - 10.04.2017 <https://github.com/jedie/django-reversion-compare/compare/v0.7.3...v0.7.4>`_:

    * Bugfix for Python 2: `compare unicode instead of bytes <https://github.com/jedie/django-reversion-compare/issues/89>`_ contributed by `Maksim Iakovlev <https://github.com/lampslave>`_

    * `remove 'Django20Warning' <https://github.com/jedie/django-reversion-compare/pull/88>`_ contributed by `Hugo Tácito <https://github.com/hugotacito>`_

    * `Add 'Finnish' localisations <https://github.com/jedie/django-reversion-compare/pull/87>`_ contributed by `Olli-Pekka Puolitaival <https://github.com/OPpuolitaival>`_

* `v0.7.3 - 08.02.2017 <https://github.com/jedie/django-reversion-compare/compare/v0.7.2...v0.7.3>`_:

    * `Fix case when model has template field which is ForeignKey <https://github.com/jedie/django-reversion-compare/pull/85>`_ contributed by `Lagovas <https://github.com/Lagovas>`_

* `v0.7.2 - 20.10.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.7.1...v0.7.2>`_:

    * Add Django v1.10 support

* `v0.7.1 - 29.08.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.7.0...v0.7.1>`_:

    * `Fix #79: missing import if **ADD_REVERSION_ADMIN != True** <https://github.com/jedie/django-reversion-compare/issues/79>`_

* `v0.7.0 - 25.08.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.6.3...v0.7.0>`_:

    * `support only django-reversion >= 2.0 <https://github.com/jedie/django-reversion-compare/pull/76>`_ based on a contribution by `mshannon1123 <https://github.com/jedie/django-reversion-compare/pull/73>`_

    * remove internal **reversion_api**

    * Use tox

* `v0.6.3 - 14.06.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.6.2...v0.6.3>`_:

    * `Remove unused and deprecated patters <https://github.com/jedie/django-reversion-compare/pull/69>`_ contributed by `codingjoe <https://github.com/codingjoe>`_

    * `Fix django 1.10 warning #66 <https://github.com/jedie/django-reversion-compare/pull/66>`_ contributed by `pypetey <https://github.com/pypetey>`_

* `v0.6.2 - 27.04.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.6.1...v0.6.2>`_:

    * `Added choices field representation #63 <https://github.com/jedie/django-reversion-compare/pull/63>`_ contributed by `amureki <https://github.com/amureki>`_

    * `Check if related model has an integer as pk for ManyToMany fields. #64 <https://github.com/jedie/django-reversion-compare/pull/64>`_ contributed by `logaritmisk <https://github.com/logaritmisk>`_

* `v0.6.1 - 16.02.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.6.0...v0.6.1>`_:

    * `pull #61 <https://github.com/jedie/django-reversion-compare/pull/61>`_: Fix error when ManyToMany relations didn't exist contributed by `Diederik van der Boor <https://github.com/vdboor>`_

* `v0.6.0 - 03.02.2016 <https://github.com/jedie/django-reversion-compare/compare/v0.5.6...v0.6.0>`_:

    * Added Dutch translation contributed by `Sae X <https://github.com/SaeX>`_

    * Add support for Django 1.9

    * Nicer boolean compare: `#57 <https://github.com/jedie/django-reversion-compare/issues/57>`_

    * Fix `#58 compare followed reverse foreign relation fields that are on a non-abstract parent class <https://github.com/jedie/django-reversion-compare/issues/58>`_ contributed by LegoStormtroopr

* `v0.5.6 - 23.09.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.5.5...v0.5.6>`_:

    * NEW: Class-Based-View to create non-admin views and greek translation contributed by `Serafeim Papastefanos <https://github.com/spapas>`_.

* `v0.5.5 - 24.07.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.5.4...v0.5.5>`_:

    * UnboundLocalError ('version') when creating deleted list in get_many_to_something() `#41 <https://github.com/jedie/django-reversion-compare/pull/41>`_

* `v0.5.4 - 22.07.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.5.3...v0.5.4>`_:

    * One to one field custom related name fix `#42 <https://github.com/jedie/django-reversion-compare/pull/42>`_ (contributed by frwickst and aemdy)

* `v0.5.3 - 13.07.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.5.2...v0.5.3>`_:

    * Update admin.py to avoid RemovedInDjango19Warning (contributed by luzfcb)

* `v0.5.2 - 14.04.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.5.1...v0.5.2>`_:

    * contributed by Samuel Spencer:

        * Added Django 1.8 support: `pull #35 <https://github.com/jedie/django-reversion-compare/pull/35>`_

        * list of changes for reverse fields incorrectly includes a "deletion" for the item that was added in: `issues #34 <https://github.com/jedie/django-reversion-compare/issues/34>`_

* `v0.5.1 - 28.02.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.5.0...v0.5.1>`_:

    * activate previous/next links and add unitests for them

* `v0.5.0 - 27.02.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.4.0...v0.5.0>`_:

    * refactory unittests, test with Django v1.7 and Python 2.7 & 3.4

* `v0.4.0 - 02.02.2015 <https://github.com/jedie/django-reversion-compare/compare/v0.3.5...v0.4.0>`_:

    * Updates for django 1.7 support

    * Add ``settings.ADD_REVERSION_ADMIN``

* v0.3.5 - 03.01.2013:

    * Remove date from version string. `issues 9 <https://github.com/jedie/django-reversion-compare/issues/9>`_

* v0.3.4 - 20.06.2012:

    * Use VersionAdmin.revision_manager rather than default_revision_manager, contributed by Mark Lavin - see: `pull request 7 <https://github.com/jedie/django-reversion-compare/pull/7>`_

    * Use logging for all debug prints, contributed by Bojan Mihelac - see: `pull request 8 <https://github.com/jedie/django-reversion-compare/pull/8>`_

* v0.3.3 - 11.06.2012:

    * Bugfix "ValueError: zero length field name in format" with Python 2.6 `issues 5 <https://github.com/jedie/django-reversion-compare/issues/5>`_

* v0.3.2 - 04.06.2012:

    * Bugfix for Python 2.6 in unified_diff(), see: `AttributeError: 'module' object has no attribute '_format_range_unified' <https://github.com/jedie/django-reversion-compare/issues/5>`_

* v0.3.1 - 01.06.2012:

    * Bugfix: force unicode in html diff

    * Bugfix in unittests

* v0.3.0 - 16.05.2012:

    * Enhanced handling of m2m changes with follow and non-follow relations.

* v0.2.2 - 15.05.2012:

    * Compare many-to-many in the right way.

* v0.2.1 - 10.05.2012:

    * Bugfix for models which has no m2m field: `https://github.com/jedie/django-reversion-compare/commit/c8e042945a6e78e5540b6ae27666f9b0cfc94880 <https://github.com/jedie/django-reversion-compare/commit/c8e042945a6e78e5540b6ae27666f9b0cfc94880>`_

* v0.2.0 - 09.05.2012:

    * many-to-many compare works, too.

* v0.1.0 - 08.05.2012:

    * First release

* v0.0.1 - 08.05.2012:

    * collect all compare stuff from old "diff" branch

    * see also: `https://github.com/etianen/django-reversion/issues/147 <https://github.com/etianen/django-reversion/issues/147>`_

-----
Links
-----

+-----------------+-------------------------------------------------------+
| Github          | `https://github.com/jedie/django-reversion-compare`_  |
+-----------------+-------------------------------------------------------+
| Python Packages | `https://pypi.org/project/django-reversion-compare/`_ |
+-----------------+-------------------------------------------------------+

.. _https://github.com/jedie/django-reversion-compare: https://github.com/jedie/django-reversion-compare
.. _https://pypi.org/project/django-reversion-compare/: https://pypi.org/project/django-reversion-compare/

--------
Donation
--------

* `paypal.me/JensDiemer <https://www.paypal.me/JensDiemer>`_

* `Flattr This! <https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2Fdjango-reversion-compare%2F>`_

* Send `Bitcoins <https://www.bitcoin.org/>`_ to `1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F <https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F>`_

------------

``Note: this file is generated from README.creole 2021-02-04 04:45:14 with "python-creole"``