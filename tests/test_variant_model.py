#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
from django.conf import settings


try:
    import django_tools
except ImportError as err:
    msg = (
              "Please install django-tools for unittests"
              " - https://github.com/jedie/django-tools/"
              " - Original error: %s"
          ) % err
    raise ImportError(msg)
from django_tools.unittest_utils.BrowserDebug import debug_response

try:
    from reversion import revisions as reversion
except ImportError:
    import reversion

try:
    from reversion.revisions import get_for_object
except ImportError:
    from reversion import get_for_object
from reversion.models import Revision

from tests.models import VariantModel

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin

from .test_utils.test_cases import BaseTestCase
from .test_utils.test_data import TestData


class VariantModelNoDataTest(BaseTestCase):
    """
    Tests with a empty VariantModel
    """
    def test_textfield(self):
        with reversion.create_revision():
            item = VariantModel.objects.create(
                text="""\
first line
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
last line"""
            )
            item.save()

        with reversion.create_revision():
            item.text = """\
first line
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis added aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
last line"""
            item.save()

        # debug_response(self.client.get("/admin/tests/variantmodel/1/history/"))
        response = self.client.get(
            "/admin/tests/variantmodel/1/history/compare/",
            data={"version_id2": 1, "version_id1": 2}
        )
        # debug_response(response) # from django-tools

        self.assertContains(response, """\
<del>-nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit</del>
<ins>+nisi ut aliquip ex ea commodo consequat. Duis added aute irure dolor in reprehenderit in voluptate velit</ins>
""")
        self.assertNotContains(response, "first line")
        self.assertNotContains(response, "last line")


class VariantModelWithDataTest(BaseTestCase):
    """
    Tests with VariantModel and existing data from TestData()
    """
    def setUp(self):
        super(VariantModelWithDataTest, self).setUp()

        self.item, self.test_data = TestData(verbose=False).create_VariantModel_data()

        queryset = get_for_object(self.item)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(VariantModel))

        self.assertEqual(VariantModel.objects.count(), 1)

        count = len(self.test_data) + 1  # incl. initial

        self.assertEqual(reversion.get_for_object(self.item).count(), count)
        self.assertEqual(Revision.objects.all().count(), count)
        self.assertEqual(len(self.version_ids), count)

    def test_all_changes(self):
        # debug_response(self.client.get("/admin/tests/variantmodel/1/history/"))

        # compare initial with last version
        response = self.client.get(
            "/admin/tests/variantmodel/1/history/compare/",
            data={
                "version_id2": 1,
                "version_id1": len(self.test_data) + 1  # incl. initial
            }
        )
        # debug_response(response) # from django-tools

        field_headlines = [
            "<h3>%s</h3>" % field_name.replace("_", " ")
            for field_name, value in self.test_data
        ]
        self.assertContainsHtml(response, *field_headlines)
        self.assertContainsHtml(response,
            "<h3>boolean</h3>",
            '<pre class="highlight"><del>- False</del> changed to <ins>+ True</ins></pre>',

            "<h3>null boolean</h3>",
            '<pre class="highlight"><del>- True</del> changed to <ins>+ None</ins></pre>',

            "<h3>char</h3>",
            "<del>- a</del>",
            "<ins>+ B</ins>",

            "<h3>text</h3>",
            "<del>- Foo &#39;one&#39;</del>",
            "<ins>+ Bar &#39;two&#39;</ins>",

            "<h3>integer</h3>",
            "<del>- 0</del>",
            "<ins>+ -1</ins>",

            "<h3>integers</h3>",
            "<del>- 1,2,3</del>",
            "<ins>+ 2,3,4</ins>",

            "<h3>positive integer</h3>",
            "<del>- 1</del>",
            "<ins>+ 3</ins>",

            "<h3>big integer</h3>",
            "<del>- -9223372036854775808</del>",
            "<ins>+ 9223372036854775807</ins>",

            "<h3>time</h3>",
            "<del>- 20:15:00</del>",
            "<ins>+ 19:30:00</ins>",

            "<h3>date</h3>",
            "<del>- 1941-05-12</del>",
            "<ins>+ 2099-12-31</ins>",

            "<h3>datetime</h3>",
            "<del>- Aug. 19, 2005, 8:13 a.m.</del>",
            "<ins>+ Jan. 1, 2000, midnight</ins>",

            "<h3>decimal</h3>",
            "<del>- 1.23456789</del>",
            "<ins>+ 3.1415926535</ins>",

            "<h3>float</h3>",
            "<del>- 2.345</del>",
            "<ins>+ 3.1415</ins>",

            "<h3>email</h3>",
            "<del>- one@foo-bar.com</del>",
            "<ins>+ two@foo-bar.com</ins>",

            "<h3>url</h3>",
            "<del>- http://www.pylucid.org/</del>",
            "<ins>+ https://github.com/jedie/</ins>",

            "<h3>filepath</h3>",
            #"<del>- %s/foo</del>" % settings.UNITTEST_TEMP_PATH,
            #"<ins>+ %s/bar</ins>" % settings.UNITTEST_TEMP_PATH,
            "<del>- %s</del>" % os.path.join(settings.UNITTEST_TEMP_PATH, 'foo'),
            "<ins>+ %s</ins>" % os.path.join(settings.UNITTEST_TEMP_PATH, 'bar'),

            "<h3>ip address</h3>",
            "<del>- 192.168.0.1</del>",
            "<ins>+ 10.0.0.0</ins>",
        )
