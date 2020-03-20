#!/usr/bin/env python

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2020 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import django
from django.apps import apps
from django.contrib.auth.models import User
from django.test import TestCase

from reversion import get_registered_models
from reversion.models import Revision, Version

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.BrowserDebug import debug_response

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
from .fixtures import Fixtures


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.fixtures = Fixtures()
        self.user = User.objects.create_superuser(
            "Test User", "nobody@local.intranet", "no password"
        )
        self.client.force_login(self.user)

    def tearDown(self):
        super().tearDown()

        Revision.objects.all().delete()
        Version.objects.all().delete()

    def assertContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertContains(response, html, html=True)
            except AssertionError as e:
                debug_response(response, msg=f"{e}")  # from django-tools
                raise

    def assertNotContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertNotContains(response, html, html=True)
            except AssertionError as e:
                debug_response(response, msg=f"{e}")  # from django-tools
                raise


class EnvironmentTest(BaseTestCase):
    def test_admin_login(self):
        response = self.client.get("/admin/")
        self.assertContainsHtml(response, "<strong>Test User</strong>")
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
