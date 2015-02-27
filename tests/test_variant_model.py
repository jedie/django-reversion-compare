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


try:
    import django_tools
except ImportError as err:
    msg = (
        "Please install django-tools for unittests"
        " - https://github.com/jedie/django-tools/"
        " - Original error: %s"
    ) % err
    raise ImportError(msg)

import reversion
from reversion import get_for_object
from reversion.models import Revision

from tests.models import VariantModel

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin

from .test_utils.test_cases import BaseTestCase
from .test_utils.test_data import TestData


class VariantModelTest(BaseTestCase):
    """
    Tests with VariantModel
    """
    def setUp(self):
        super(VariantModelTest, self).setUp()

        test_data = TestData(verbose=False)
#        test_data = TestData(verbose=True)
        self.item = test_data.create_VariantModel_data()

        queryset = get_for_object(self.item)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(VariantModel))

        self.assertEqual(VariantModel.objects.count(), 1)

        self.assertEqual(reversion.get_for_object(self.item).count(), 1)
        self.assertEqual(Revision.objects.all().count(), 1)

    def test_textfield(self):
        with reversion.create_revision():
            self.item.text = """\
first line
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
last line"""
            self.item.save()

        with reversion.create_revision():
            self.item.text = """\
first line
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis added aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
last line"""
            self.item.save()

        queryset = get_for_object(self.item)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get(
            "/admin/tests/variantmodel/%s/history/compare/" % self.item.pk,
            data={"version_id2":version_ids[0], "version_id1":version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContains(response, """\
<del>-nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit</del>
<ins>+nisi ut aliquip ex ea commodo consequat. Duis added aute irure dolor in reprehenderit in voluptate velit</ins>
""")
        self.assertNotContains(response, "first line")
        self.assertNotContains(response, "last line")


