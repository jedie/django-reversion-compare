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
import datetime


if __name__ == "__main__":
    # run unittest directly by execute manage.py from test project
    import os, sys
    os.environ['DJANGO_SETTINGS_MODULE'] = 'reversion_compare_test_project.settings'
    from django.core import management
    management.call_command("test", "reversion_compare", verbosity=2, traceback=True, interactive=False)
#    management.call_command("test", "reversion_compare.FactoryCarModelTest", verbosity=2, traceback=True, interactive=False)
#    management.call_command("test", "reversion_compare.PersonPetModelTest", verbosity=2, traceback=True, interactive=False)
    sys.exit()

from django.db.models.loading import get_models, get_app
from django.test import TestCase
from django.contrib.auth.models import User

# 
try:
    import django_tools
except ImportError, err:
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

from reversion_compare_test_project.reversion_compare_test_app.models import SimpleModel, Person, Pet, \
    Factory, Car, VariantModel

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
import reversion_compare_test_project.reversion_compare_test_app.admin
from reversion_compare_test_project.reversion_compare_test_app.admin import custom_revision_manager


class TestData(object):
    """
    Collection of all test data creation method.
    This will be also used from external scripts, too!
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def create_all(self):
        """
        simple call all create_*_data() methods
        """
        for method_name in dir(self):
            if method_name.startswith("create_") and method_name.endswith("_data"):
                if self.verbose:
                    print "_"*79
                    print " *** %s ***" % method_name
                func = getattr(self, method_name)
                func()

    def create_Simple_data(self):
        with reversion.create_revision():
            item1 = SimpleModel.objects.create(text="version one")

        if self.verbose:
            print "version 1:", item1

        with reversion.create_revision():
            item1.text = "version two"
            item1.save()
            reversion.set_comment("simply change the CharField text.")

        if self.verbose:
            print "version 2:", item1

        return item1

    def create_FactoryCar_data(self):
        with reversion.create_revision():
            manufacture = Factory.objects.create(name="factory one")
            supplier1 = Factory.objects.create(name="always the same supplier")
            supplier2 = Factory.objects.create(name="would be deleted supplier")
            supplier3 = Factory.objects.create(name="would be removed supplier")
            car = Car.objects.create(
                name="motor-car one",
                manufacturer=manufacture
            )
            car.supplier.add(supplier1, supplier2, supplier3)
            car.save()
            reversion.set_comment("initial version 1")

        if self.verbose:
            print "version 1:", car
            # motor-car one from factory one supplier(s): always the same supplier, would be deleted supplier, would be removed supplier

        """ 1 to 2 diff:

        "manufacture" ForeignKey:
            "factory one" -> "factory I"

        "supplier" ManyToManyField:
            + new, would be renamed supplier
            - would be deleted supplier
            - would be removed supplier
            = always the same supplier
        """

        with reversion.create_revision():
            manufacture.name = "factory I"
            manufacture.save()
            supplier2.delete()
            supplier4 = Factory.objects.create(name="new, would be renamed supplier")
            car.supplier.add(supplier4)
            car.supplier.remove(supplier3)
            car.save()
            reversion.set_comment("version 2: change ForeignKey and ManyToManyField.")

        if self.verbose:
            print "version 2:", car
            # motor-car one from factory I supplier(s): always the same supplier, new, would be renamed supplier

        """ 2 to 3 diff:
        
        "name" CharField:
            "motor-car one" -> "motor-car II"

        "manufacture" ForeignKey:
            "factory I" -> "factory II"

        "supplier" ManyToManyField:
            new, would be renamed supplier -> not new anymore supplier
            = always the same supplier
        """

        with reversion.create_revision():
            car.name = "motor-car II"
            manufacture.name = "factory II"
            supplier4.name = "not new anymore supplier"
            supplier4.save()
            car.save()
            reversion.set_comment("version 3: change CharField, ForeignKey and ManyToManyField.")

        if self.verbose:
            print "version 3:", car
            # version 3: motor-car II from factory II supplier(s): always the same supplier, not new anymore supplier
        
        return car

    def create_PersonPet_data(self):
        with reversion.create_revision():
            pet1 = Pet.objects.create(name="would be changed pet")
            pet2 = Pet.objects.create(name="would be deleted pet")
            pet3 = Pet.objects.create(name="would be removed pet")
            pet4 = Pet.objects.create(name="always the same pet")
            person = Person.objects.create(name="Dave")
            person.pets.add(pet1, pet2, pet3, pet4)
            person.save()
            reversion.set_comment("initial version 1")

        if self.verbose:
            print "version 1:", person, person.pets.all()
            # Dave [<Pet: would be changed pet>, <Pet: would be deleted pet>, <Pet: would be removed pet>, <Pet: always the same pet>]

        """ 1 to 2 diff:

        "pets" ManyToManyField:
            would be changed pet -> Is changed pet
            - would be removed pet
            - would be deleted pet
            = always the same pet
        """

        with reversion.create_revision():
            pet1.name = "Is changed pet"
            pet1.save()
            pet2.delete()
            person.pets.remove(pet3)
            person.save()
            reversion.set_comment("version 2: change follow related pets.")

        if self.verbose:
            print "version 2:", person, person.pets.all()
            # Dave [<Pet: Is changed pet>, <Pet: always the same pet>]
            
        return pet1, pet2, person

    def create_VariantModel_data(self):
        with reversion.create_revision():
            item = VariantModel.objects.create(
                integer = 0,
                positive_integer = 0,
                big_integer = 0,
                time = datetime.time(hour=20, minute=15),
                date = datetime.date(year=1941, month=5, day=12), # Z3 was presented in germany ;)
                # PyLucid v0.0.1 release date:
                datetime = datetime.datetime(year=2005, month=8, day=19, hour=8, minute=13, second=24),
                decimal = 0,
                float = 0,
                ip_address = "192.168.0.1",
            )

        if self.verbose:
            print "version 1:", item

        return item

class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        
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

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        
        Revision.objects.all().delete()
        Version.objects.all().delete()

    def assertContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertContains(response, html, html=True)
            except AssertionError, e:
                debug_response(response, msg="%s" % e) # from django-tools
                raise

    def assertNotContainsHtml(self, response, *args):
        for html in args:
            try:
                self.assertNotContains(response, html, html=True)
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
        default_registered = len(reversion.get_registered_models())
        custom_registered = len(custom_revision_manager.get_registered_models())
        self.assertEqual(default_registered + custom_registered, len(models))


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
        response = self.client.get("/admin/reversion_compare_test_app/simplemodel/%s/history/" % self.item1.pk)
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
            "/admin/reversion_compare_test_app/simplemodel/%s/history/compare/" % self.item1.pk,
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


class FactoryCarModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car
        
    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """
    def setUp(self):
        super(FactoryCarModelTest, self).setUp()

        test_data = TestData(verbose=False)
#        test_data = TestData(verbose=True)
        self.car = test_data.create_FactoryCar_data()
        
        queryset = get_for_object(self.car)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(Factory))
        self.assertTrue(reversion.is_registered(Car))

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(len(self.version_ids), 3)
        self.assertEqual(Version.objects.all().count(), 11)

    def test_select_compare(self):
        response = self.client.get("/admin/reversion_compare_test_app/car/%s/history/" % self.car.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
        )
        
    def test_diff1(self):
        response = self.client.get(
            "/admin/reversion_compare_test_app/car/%s/history/compare/" % self.car.pk,
            data={"version_id2":self.version_ids[1], "version_id1":self.version_ids[2]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<h3>supplier<sup class="follow">*</sup></h3>',
            '''
            <p class="highlight">   
                <del>- would be deleted supplier</del><br />
                <del>- would be removed supplier</del><br />
                <ins>+ new, would be renamed supplier</ins><br />
                always the same supplier<sup class="follow">*</sup><br />
            </p>
            ''',
            '<h4 class="follow">Note:</h4>', # info for non-follow related informations
            '<blockquote>version 2: change ForeignKey and ManyToManyField.</blockquote>', # edit comment
        )
        
    def test_diff2(self):
        response = self.client.get(
            "/admin/reversion_compare_test_app/car/%s/history/compare/" % self.car.pk,
            data={"version_id2":self.version_ids[0], "version_id1":self.version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            "<del>- motor-car one</del>",
            "<ins>+ motor-car II</ins>",

            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<h3>supplier<sup class="follow">*</sup></h3>',
            '''
            <p class="highlight">   
                <del>new, would be renamed supplier</del> &rarr; <ins>not new anymore supplier</ins><br />
                always the same supplier<sup class="follow">*</sup><br />
            </p>
            ''',
            '<h4 class="follow">Note:</h4>', # info for non-follow related informations
            '<blockquote>version 3: change CharField, ForeignKey and ManyToManyField.</blockquote>', # edit comment
        )


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

        test_data = TestData(verbose=False)
#        test_data = TestData(verbose=True)
        self.pet1, self.pet2, self.person = test_data.create_PersonPet_data()
        
        queryset = get_for_object(self.person)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(Pet))
        self.assertTrue(reversion.is_registered(Person))

        self.assertEqual(Pet.objects.count(), 3)

        self.assertEqual(reversion.get_for_object(self.pet1).count(), 2)
        self.assertEqual(Revision.objects.all().count(), 2)

    def test_select_compare(self):
        response = self.client.get("/admin/reversion_compare_test_app/person/%s/history/" % self.person.pk)
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
            "/admin/reversion_compare_test_app/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":self.version_ids[0], "version_id1":self.version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            """
            <p class="highlight">
                <del>would be changed pet</del> &rarr; <ins>Is changed pet</ins><br />
                <del>- would be deleted pet</del><br />
                <del>- would be removed pet</del><br />
                always the same pet<br />
            </p>
            """,
            "<blockquote>version 2: change follow related pets.</blockquote>", # edit comment
        )
        self.assertNotContainsHtml(response,
            "<h3>name</h3>", # person name doesn't changed 
            'class="follow"'# All fields are under reversion control
        )

    def test_add_m2m(self):
        with reversion.create_revision():
            new_pet = Pet.objects.create(name="added pet")
            self.person.pets.add(new_pet)
            self.person.save()
            reversion.set_comment("version 3: add a pet")

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 13)

        queryset = get_for_object(self.person)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get("/admin/reversion_compare_test_app/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
        )

        response = self.client.get(
            "/admin/reversion_compare_test_app/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":version_ids[0], "version_id1":version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            """
            <p class="highlight">
                <ins>+ added pet</ins><br />
                Is changed pet<br />
                always the same pet<br />
            </p>
            """,
            "<blockquote>version 3: add a pet</blockquote>", # edit comment
        )
        self.assertNotContainsHtml(response,
            "<h3>name</h3>", # person name doesn't changed 
            'class="follow"'# All fields are under reversion control
        )

    def test_m2m_not_changed(self):
        with reversion.create_revision():
            self.person.name = "David"
            self.person.save()
            reversion.set_comment("version 3: change the name")

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 12)

        queryset = get_for_object(self.person)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get("/admin/reversion_compare_test_app/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
        )

        response = self.client.get(
            "/admin/reversion_compare_test_app/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":version_ids[0], "version_id1":version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '''
            <p><pre class="highlight">
            <del>- Dave</del>
            <ins>+ David</ins>
            </pre></p>
            ''',
            "<blockquote>version 3: change the name</blockquote>", # edit comment
        )
        self.assertNotContainsHtml(response,
            "pet", 
            'class="follow"'# All fields are under reversion control
        )


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
            "/admin/reversion_compare_test_app/variantmodel/%s/history/compare/" % self.item.pk,
            data={"version_id2":version_ids[0], "version_id1":version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContains(response, """\
<del>-nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit</del>
<ins>+nisi ut aliquip ex ea commodo consequat. Duis added aute irure dolor in reprehenderit in voluptate velit</ins>
""")
        self.assertNotContains(response, "first line")
        self.assertNotContains(response, "last line")