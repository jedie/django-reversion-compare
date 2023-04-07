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
import warnings

from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.auth.models import User
from django.test import TestCase
from reversion.models import Revision, Version

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
from reversion_compare_project.utils.fixtures import Fixtures


class BaseTestCase(HtmlAssertionMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.fixtures = Fixtures()
        self.user = User.objects.create_superuser("Test User", "nobody@local.intranet", "no password")
        self.client.force_login(self.user)

    def tearDown(self):
        super().tearDown()

        Revision.objects.all().delete()
        Version.objects.all().delete()

    def assertContainsHtml(self, response, *args):
        warnings.warn('Use assert_html_parts()', DeprecationWarning)
        self.assert_html_parts(response, parts=args)

    def assertNotContainsHtml(self, response, *args):
        warnings.warn('Use assert_parts_not_in_html()', DeprecationWarning)
        self.assert_parts_not_in_html(response, parts=args)
