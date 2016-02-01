#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

from django.apps import apps
from django.test import TestCase


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

from reversion.models import Revision, Version

from reversion_compare import helpers

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
from tests.admin import custom_revision_manager
from .test_data import TestData


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.test_data = TestData()
        self.user = self.test_data.create_testuser_data()

        # Log the user in.
        self.client.login(
            username=self.test_data.TEST_USERNAME,
            password=self.test_data.TEST_USERPASS
        )

        # http://code.google.com/p/google-diff-match-patch/
        if helpers.google_diff_match_patch:
            # run all tests without google-diff-match-patch as default
            # some tests can activate it temporary
            helpers.google_diff_match_patch = False
            self.google_diff_match_patch = True
        else:
            self.google_diff_match_patch = False

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

        Revision.objects.all().delete()
        Version.objects.all().delete()

    def assertContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertContains(response, html, html=True)
            except AssertionError as e:
                debug_response(response, msg="%s" % e) # from django-tools
                raise

    def assertNotContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertNotContains(response, html, html=True)
            except AssertionError as e:
                debug_response(response, msg="%s" % e) # from django-tools
                raise


class EnvironmentTest(BaseTestCase):
    def test_admin_login(self):
        response = self.client.get("/admin/")
        self.assertContainsHtml(response, "<strong>test</strong>")
        self.assertEqual(response.status_code, 200)

    def test_model_registering(self):
        test_app_config = apps.get_app_config(app_label="tests")
        models = test_app_config.get_models(
            include_auto_created=False, include_deferred=False, include_swapped=False
        )
        default_registered = len(reversion.get_registered_models())
        custom_registered = len(custom_revision_manager.get_registered_models())
        self.assertEqual(default_registered + custom_registered, len(tuple(models)))
