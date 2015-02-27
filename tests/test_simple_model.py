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

import datetime

from django.core.urlresolvers import reverse
from django.db.models.loading import get_models, get_app
from django.test import TestCase
from django.contrib.auth.models import User



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

import reversion
from reversion import get_for_object
from reversion.models import Revision, Version

from reversion_compare import helpers

from .test_utils.test_cases import BaseTestCase
from .models import SimpleModel
from .test_utils.test_data import TestData


class SimpleModelTest(BaseTestCase):
    """
    unittests that used reversion_compare_test_app.models.SimpleModel

    Tests for the basic functions.
    """
    def setUp(self):
        super(SimpleModelTest, self).setUp()
        test_data = TestData(verbose=False)
#        test_data = TestData(verbose=True)
        self.item1 = test_data.create_Simple_data()

        queryset = get_for_object(self.item1)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(SimpleModel))

        self.assertEqual(SimpleModel.objects.count(), 1)
        self.assertEqual(SimpleModel.objects.all()[0].text, "version two")

        self.assertEqual(reversion.get_for_object(self.item1).count(), 2)
        self.assertEqual(Revision.objects.all().count(), 2)
        self.assertEqual(len(self.version_ids), 2)
        self.assertEqual(Version.objects.all().count(), 2)

    def test_select_compare(self):
        response = self.client.get("/admin/tests/simplemodel/%s/history/" % self.item1.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
        )

    def test_diff(self):
        response = self.client.get(
            "/admin/tests/simplemodel/%s/history/compare/" % self.item1.pk,
            data={"version_id2":self.version_ids[0], "version_id1":self.version_ids[1]}
        )
        #debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '<del>- version one</del>',
            '<ins>+ version two</ins>',
            '<blockquote>simply change the CharField text.</blockquote>', # edit comment
        )

        if self.google_diff_match_patch:
            # google-diff-match-patch is available
            helpers.google_diff_match_patch = True
            try:
                self.assertContainsHtml(response,
                    """
                    <p><span>version </span>
                    <del style="background:#ffe6e6;">one</del>
                    <ins style="background:#e6ffe6;">two</ins>
                    </p>
                    """,
                    '<blockquote>simply change the CharField text.</blockquote>', # edit comment
                )
            finally:
                helpers.google_diff_match_patch = False # revert

