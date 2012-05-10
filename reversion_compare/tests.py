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

from __future__ import with_statement

import datetime, os

if __name__ == "__main__":
    # run unittest directly by execute manage.py from test project
    import sys, subprocess, reversion_compare_test_project
    abspath = os.path.abspath(os.path.dirname(reversion_compare_test_project.__file__))
    #subprocess.call(["./manage.py", "diffsettings"], cwd=abspath)
    subprocess.call(["./manage.py", "test", "reversion_compare", "--verbosity=1"], cwd=abspath)
    sys.exit()

from django.db import models
from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.decorators import decorator_from_middleware
from django.http import HttpResponse
from django.utils.unittest import skipUnless

# https://github.com/jedie/django-tools/
from django_tools.unittest_utils.BrowserDebug import debug_response

import reversion
from reversion.revisions import RegistrationError, RevisionManager, RevisionManagementError
from reversion.models import Revision, Version, VERSION_ADD, VERSION_CHANGE, VERSION_DELETE
from reversion.middleware import RevisionMiddleware

from reversion_compare.admin import CompareVersionAdmin
from reversion_compare_test_project.reversion_compare_test_app.models import SimpleModel



class BaseTestCase(TestCase):

#    urls = "reversion_compare.tests"

    def setUp(self):
#        self.old_TEMPLATE_DIRS = settings.TEMPLATE_DIRS
#        settings.TEMPLATE_DIRS = (
#            os.path.join(os.path.dirname(admin.__file__), "templates"),
#        )

        self.user = User(
            username="foo",
            is_staff=True,
            is_superuser=True,
        )
        self.user.set_password("bar")
        self.user.save()
        # Log the user in.
        self.client.login(
            username="foo",
            password="bar",
        )

#        if hasattr(self, "settings"):
#            # HACK: Without this the client won't log in, for some reason.
#            with self.settings(
#                INSTALLED_APPS=tuple(
#                    set(tuple(settings.INSTALLED_APPS) + ("django.contrib.sessions",))
#                )):
#                self.client.login(
#                    username="foo",
#                    password="bar",
#                )
#        else:


#    def tearDown(self):
#        self.client.logout()
#        self.user.delete()
#        del self.user
#        ChildTestAdminModel.objects.all().delete()
#        settings.TEMPLATE_DIRS = self.old_TEMPLATE_DIRS

class VersionCompareSimpleModelTest(BaseTestCase):
    def setUp(self):
        super(VersionCompareSimpleModelTest, self).setUp()
        with reversion.create_revision():
            self.item1 = SimpleModel.objects.create(text="version one")
        with reversion.create_revision():
            self.item1.text = "version two"
            self.item1.save()

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(SimpleModel))

        self.assertEqual(SimpleModel.objects.count(), 1)
        self.assertEqual(SimpleModel.objects.all()[0].text, "version two")




    def testRevisionSavedOnPost(self):


#        
#            item = TestModel1(name="test1")
#            item.save()
#
#        obj_pk = item.pk

        response = self.client.get("/admin/reversion_compare_test_app/simplemodel/%s/history/" % self.item1.pk)
        debug_response(response) # from django-tools

#        response = self.client.get("/admin/auth/testmodel1/%s/history/" % obj_pk)

#        debug_response(response)

#        self.assertContains(response, "child instance1 version2")

"""
        
        # Create an instance via the admin.
        response = self.client.post("/admin/auth/childtestadminmodel/add/", {
            "parent_name": "parent instance1 version1",
            "child_name": "child instance1 version1",
            "_continue": 1,
        })
        self.assertEqual(response.status_code, 302)
        obj_pk = response["Location"].split("/")[-2]
        obj = ChildTestAdminModel.objects.get(id=obj_pk)
        # Check that a version is created.
        versions = reversion.get_for_object(obj)
        self.assertEqual(versions.count(), 1)
        self.assertEqual(versions[0].field_dict["parent_name"], "parent instance1 version1")
        self.assertEqual(versions[0].field_dict["child_name"], "child instance1 version1")
        # Save a new version.
        response = self.client.post("/admin/auth/childtestadminmodel/%s/" % obj_pk, {
            "parent_name": "parent instance1 version2",
            "child_name": "child instance1 version2",
            "_continue": 1,
        })
        self.assertEqual(response.status_code, 302)
        # Check that a version is created.
        versions = reversion.get_for_object(obj)
        self.assertEqual(versions.count(), 2)
        self.assertEqual(versions[0].field_dict["parent_name"], "parent instance1 version2")
        self.assertEqual(versions[0].field_dict["child_name"], "child instance1 version2")
        # Check that the versions can be listed.
        response = self.client.get("/admin/auth/childtestadminmodel/%s/history/" % obj_pk)
        self.assertContains(response, "child instance1 version2")
        self.assertContains(response, "child instance1 version1")
        # Check that a version can be rolled back.
        response = self.client.post("/admin/auth/childtestadminmodel/%s/history/%s/" % (obj_pk, versions[1].pk), {
            "parent_name": "parent instance1 version3",
            "child_name": "child instance1 version3",
        })
        self.assertEqual(response.status_code, 302)
        # Check that a version is created.
        versions = reversion.get_for_object(obj)
        self.assertEqual(versions.count(), 3)
        self.assertEqual(versions[0].field_dict["parent_name"], "parent instance1 version3")
        self.assertEqual(versions[0].field_dict["child_name"], "child instance1 version3")
        # Check that a deleted version can be viewed.
        obj.delete()
        response = self.client.get("/admin/auth/childtestadminmodel/recover/")
        self.assertContains(response, "child instance1 version3")
        # Check that a deleted version can be recovered.
        response = self.client.post("/admin/auth/childtestadminmodel/recover/%s/" % versions[0].pk, {
            "parent_name": "parent instance1 version4",
            "child_name": "child instance1 version4",
        })
        obj = ChildTestAdminModel.objects.get(id=obj_pk)

"""
