#!/usr/bin/env python
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
    import os, sys
    os.environ['DJANGO_SETTINGS_MODULE'] = 'reversion_compare_test_project.settings'
    from django.core import management
    management.call_command("test", "reversion_compare", verbosity=2, traceback=True, interactive=False)
#    management.call_command("test", "reversion_compare.PersonPetModelTest", verbosity=2, traceback=True, interactive=False)
    sys.exit()

from django.db.models.loading import get_models, get_app
from django.test import TestCase
from django.contrib.auth.models import User

# https://github.com/jedie/django-tools/
from django_tools.unittest_utils.BrowserDebug import debug_response

import reversion
from reversion.models import Revision, Version

from reversion_compare import helpers

from reversion_compare_test_project.reversion_compare_test_app.models import SimpleModel, Person, Pet

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
import reversion_compare_test_project.reversion_compare_test_app.admin


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User(username="test_user", is_staff=True, is_superuser=True)
        self.user.set_password("foobar")
        self.user.save()
        # Log the user in.
        self.client.login(username="test_user", password="foobar")

        # http://code.google.com/p/google-diff-match-patch/
        if helpers.google_diff_match_patch:
            # run all tests without google-diff-match-patch as default
            # some tests can activate it temporary
            helpers.google_diff_match_patch = False
            self.google_diff_match_patch = True
        else:
            self.google_diff_match_patch = False

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
        test_app = get_app(app_label="reversion_compare_test_app")
        models = get_models(app_mod=test_app, include_auto_created=False, include_deferred=False, only_installed=True)
        self.assertEqual(len(reversion.get_registered_models()), len(models))


class SimpleModelTest(BaseTestCase):
    """
    unittests that used reversion_compare_test_app.models.SimpleModel
    """
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

        if self.google_diff_match_patch:
            # google-diff-match-patch is available
            helpers.google_diff_match_patch = True
            try:
                self.assertContainsHtml(response,
                    '<p><span>version </span>'
                    '<del style="background:#ffe6e6;">one</del>'
                    '<ins style="background:#e6ffe6;">two</ins></p>'
                )
            finally:
                helpers.google_diff_match_patch = False # revert


class PersonPetModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Person
        reversion_compare_test_app.models.Pet
        
    Person & Pet are registered with the follow information, so that
    related data would be also stored in django-reversion

    see "Advanced model registration" here:
        https://github.com/etianen/django-reversion/wiki/Low-level-API
    """
    def setUp(self):
        super(PersonPetModelTest, self).setUp()

        with reversion.create_revision():
            self.pet1 = Pet.objects.create(name="Catworth")
            self.pet2 = Pet.objects.create(name="Dogwoth")
            self.person = Person.objects.create(name="Dave")
            self.person.pets.add(self.pet1, self.pet2)

#        print "version 1:", self.person, self.person.pets.all()
        # Dave [<Pet: Catworth>, <Pet: Dogwoth>]

        with reversion.create_revision():
            self.pet1.name = "Catworth the second"
            self.pet1.save()
            self.pet2.save()
            self.pet2.delete()
            self.person.save()

#        print "version 2:", self.person, self.person.pets.all()
        # Dave [<Pet: Catworth the second>]

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(Pet))
        self.assertTrue(reversion.is_registered(Person))

        self.assertEqual(Pet.objects.count(), 1)
        self.assertEqual(Pet.objects.all()[0].name, "Catworth the second")

        self.assertEqual(reversion.get_for_object(self.pet1).count(), 2)
        self.assertEqual(Revision.objects.all().count(), 2)
        self.assertEqual(Version.objects.all().count(), 6)

    def test_select_compare(self):
        response = self.client.get("/admin/reversion_compare_test_app/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="5" style="visibility:hidden" />',
            '<input type="radio" name="version_id2" value="5" checked="checked" />',
            '<input type="radio" name="version_id1" value="3" checked="checked" />',
            '<input type="radio" name="version_id2" value="3" />',
        )

    def test_diff(self):
        response = self.client.get(
            "/admin/reversion_compare_test_app/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":5, "version_id1":3}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '''
            <p class="highlight">
            <del>- Catworth</del><br />
            <del>- Dogwoth</del><br />
            <ins>+ Catworth the second</ins><br />
            </p>
            '''
        )
        self.assertNotContains(response, "+ Dogwoth")

    def test_add_m2m(self):
        with reversion.create_revision():
            self.pet3 = Pet.objects.create(name="Mousewoth")
            self.person.pets.add(self.pet3)

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 9)

        #print "version 3:", self.person, self.person.pets.all()
        # Dave [<Pet: Catworth the second>, <Pet: Mousewoth>]

        response = self.client.get("/admin/reversion_compare_test_app/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="7" style="visibility:hidden" />',
            '<input type="radio" name="version_id2" value="7" checked="checked" />',
            '<input type="radio" name="version_id1" value="5" checked="checked" />',
            '<input type="radio" name="version_id2" value="5" />',
            '<input type="radio" name="version_id1" value="3" />',
            '<input type="radio" name="version_id2" value="3" />',
        )

        response = self.client.get(
            "/admin/reversion_compare_test_app/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":7, "version_id1":5}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '<p class="highlight">'
            '<ins>+ Mousewoth</ins><br />'
            '</p>'
        )
        self.assertNotContains(response, "Dogwoth")
        self.assertNotContains(response, "Catworth")
        self.assertNotContains(response, "<del>")

    def test_m2m_not_changed(self):
        with reversion.create_revision():
            self.person.name = "David"
            self.person.save()

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 8)

        #print "version 3:", self.person, self.person.pets.all()
        # David [<Pet: Catworth the second>]

        response = self.client.get("/admin/reversion_compare_test_app/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="7" style="visibility:hidden" />',
            '<input type="radio" name="version_id2" value="7" checked="checked" />',
            '<input type="radio" name="version_id1" value="5" checked="checked" />',
            '<input type="radio" name="version_id2" value="5" />',
            '<input type="radio" name="version_id1" value="3" />',
            '<input type="radio" name="version_id2" value="3" />',
        )

        response = self.client.get(
            "/admin/reversion_compare_test_app/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":7, "version_id1":5}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '''
            <p><pre class="highlight">
            <del>- Dave</del>
            <ins>+ David</ins>
            </pre></p>
            '''
        )
        self.assertNotContains(response, "Dogwoth")
        self.assertNotContains(response, "Catworth")
