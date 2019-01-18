#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2017 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import django
from django.apps import apps
from django.test import TestCase

from reversion import get_registered_models
from reversion.models import Revision, Version

try:
    import django_tools
except ImportError as err:
    msg = (
        "Please install django-tools for unittests" " - https://github.com/jedie/django-tools/" " - Original error: %s"
    ) % err
    raise ImportError(msg)

from django_tools.unittest_utils.BrowserDebug import debug_response

from reversion_compare import helpers

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
from .fixtures import Fixtures


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.fixtures = Fixtures()
        self.user = self.fixtures.create_testuser_data()

        # Log the user in.
        self.client.login(username=self.fixtures.TEST_USERNAME, password=self.fixtures.TEST_USERPASS)

        # http://code.google.com/p/google-diff-match-patch/
        if hasattr(helpers, "diff_match_patch"):
            # run all tests without google-diff-match-patch as default
            # some tests can activate it temporary
            helpers.dmp = None

    def activate_google_diff_match_patch(self):
        assert hasattr(helpers, "diff_match_patch")
        helpers.dmp = helpers.diff_match_patch()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

        Revision.objects.all().delete()
        Version.objects.all().delete()

    def assertContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertContains(response, html, html=True)
            except AssertionError as e:
                debug_response(response, msg="%s" % e)  # from django-tools
                raise

    def assertNotContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertNotContains(response, html, html=True)
            except AssertionError as e:
                debug_response(response, msg="%s" % e)  # from django-tools
                raise


class EnvironmentTest(BaseTestCase):
    def test_admin_login(self):
        response = self.client.get("/admin/")
        self.assertContainsHtml(response, "<strong>test</strong>")
        self.assertEqual(response.status_code, 200)

    def test_model_registering(self):
        test_app_config = apps.get_app_config(app_label="reversion_compare_tests")
        if django.VERSION < (1, 10):
            models = test_app_config.get_models(
                include_auto_created=False, include_deferred=False, include_swapped=False
            )
        else:
            # Django >= v1.10
            models = test_app_config.get_models(include_auto_created=False, include_swapped=False)
        default_registered = len(list(get_registered_models()))
        self.assertEqual(default_registered, len(tuple(models)))
