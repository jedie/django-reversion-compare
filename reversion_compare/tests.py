# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    I used the setup from reversion_compare_test_project !
    
    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # run unittest directly by execute manage.py from test project
    import os, sys, subprocess, reversion_compare_test_project
    abspath = os.path.abspath(os.path.dirname(reversion_compare_test_project.__file__))
    #subprocess.call(["./manage.py", "diffsettings"], cwd=abspath)
    subprocess.call(["./manage.py", "test", "reversion_compare", "--verbosity=1"], cwd=abspath)
    sys.exit()

from django.test import TestCase
from django.contrib.auth.models import User

# https://github.com/jedie/django-tools/
from django_tools.unittest_utils.BrowserDebug import debug_response

import reversion
from reversion.models import Revision, Version

from reversion_compare_test_project.reversion_compare_test_app.models import SimpleModel

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
import reversion_compare_test_project.reversion_compare_test_app.admin


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User(username="test_user", is_staff=True, is_superuser=True)
        self.user.set_password("foobar")
        self.user.save()
        # Log the user in.
        self.client.login(username="test_user", password="foobar")

    def assertContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertContains(response, html, html=True)
            except AssertionError, e:
                debug_response(response, msg="%s" % e) # from django-tools
                raise


class EnvironmentTest(BaseTestCase):
    def test_admin_login(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<strong>test_user</strong>")
        #debug_response(response) # from django-tools

    def test_model_registering(self):
        # depends on the model count!
        self.assertEqual(len(reversion.get_registered_models()), 10)


class SimpleModelTest(BaseTestCase):
    def setUp(self):
        super(SimpleModelTest, self).setUp()

        with reversion.create_revision():
            self.item1 = SimpleModel.objects.create(text="version one")

        with reversion.create_revision():
            self.item1.text = "version two"
            self.item1.save()

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(SimpleModel))

        self.assertEqual(SimpleModel.objects.count(), 1)
        self.assertEqual(SimpleModel.objects.all()[0].text, "version two")

        self.assertEqual(reversion.get_for_object(self.item1).count(), 2)
        self.assertEqual(Revision.objects.all().count(), 2)
        self.assertEqual(Version.objects.all().count(), 2)

    def test_select_compare(self):
        response = self.client.get("/admin/reversion_compare_test_app/simplemodel/%s/history/" % self.item1.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="2" style="visibility:hidden" />',
            '<input type="radio" name="version_id2" value="2" checked="checked" />',
            '<input type="radio" name="version_id1" value="1" checked="checked" />',
            '<input type="radio" name="version_id2" value="1" />',
        )

    def test_diff(self):
        response = self.client.get(
            "/admin/reversion_compare_test_app/simplemodel/%s/history/compare/" % self.item1.pk,
            data={"version_id2":2, "version_id1":1}
        )
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<del>- version one</del>',
            '<ins>+ version two</ins>',
        )

