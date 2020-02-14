#!/usr/bin/env python

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


from reversion import create_revision, is_registered, set_comment
from reversion.models import Revision, Version

from reversion_compare_tests.models import Person, Pet
from .utils.fixtures import Fixtures
# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin
from .utils.test_cases import BaseTestCase


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
        super().setUp()

        fixtures = Fixtures(verbose=False)
        # fixtures = Fixtures(verbose=True)
        self.pet1, self.pet2, self.person = fixtures.create_PersonPet_data()

        queryset = Version.objects.get_for_object(self.person)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(is_registered(Pet))
        self.assertTrue(is_registered(Person))

        self.assertEqual(Pet.objects.count(), 3)

        self.assertEqual(Version.objects.get_for_object(self.pet1).count(), 2)
        self.assertEqual(Revision.objects.all().count(), 2)

    def test_select_compare(self):
        response = self.client.get(f"/admin/reversion_compare_tests/person/{self.person.pk}/history/")
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{self.version_ids[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{self.version_ids[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[1]:d}" />',
        )

    def test_diff(self):
        response = self.client.get(
            f"/admin/reversion_compare_tests/person/{self.person.pk}/history/compare/",
            data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]},
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            """
            <p class="highlight">
                <del>would be changed pet</del> &rarr; <ins>Is changed pet</ins><br />
                <del>- would be deleted pet</del><br />
                <del>- would be removed pet</del><br />
                always the same pet<br />
            </p>
            """,
            "<blockquote>version 2: change follow related pets.</blockquote>",  # edit comment
        )
        self.assertNotContainsHtml(
            response,
            "<h3>name</h3>",  # person name doesn't changed
            'class="follow"',  # All fields are under reversion control
        )

    def test_add_m2m(self):
        with create_revision():
            new_pet = Pet.objects.create(name="added pet")
            self.person.pets.add(new_pet)
            self.person.save()
            set_comment("version 3: add a pet")

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 12)

        queryset = Version.objects.get_for_object(self.person)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get(f"/admin/reversion_compare_tests/person/{self.person.pk}/history/")
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{version_ids[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{version_ids[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{version_ids[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{version_ids[1]:d}" />',
            f'<input type="radio" name="version_id2" value="{version_ids[2]:d}" />',
            f'<input type="radio" name="version_id2" value="{version_ids[2]:d}" />',
        )

        response = self.client.get(
            f"/admin/reversion_compare_tests/person/{self.person.pk}/history/compare/",
            data={"version_id2": version_ids[0], "version_id1": version_ids[1]},
        )
        # debug_response(response) # from django-tools

        self.assertContainsHtml(
            response,
            """
            <p class="highlight">
                <ins>+ added pet</ins><br />
                Is changed pet<br />
                always the same pet<br />
            </p>
            """,
            "<blockquote>version 3: add a pet</blockquote>",  # edit comment
        )
        self.assertNotContainsHtml(
            response,
            "<h3>name</h3>",  # person name doesn't changed
            'class="follow"',  # All fields are under reversion control
        )

    def test_m2m_not_changed(self):
        with create_revision():
            self.person.name = "David"
            self.person.save()
            set_comment("version 3: change the name")

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 11)

        queryset = Version.objects.get_for_object(self.person)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get(f"/admin/reversion_compare_tests/person/{self.person.pk}/history/")
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{version_ids[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{version_ids[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{version_ids[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{version_ids[1]:d}" />',
            f'<input type="radio" name="version_id2" value="{version_ids[2]:d}" />',
            f'<input type="radio" name="version_id2" value="{version_ids[2]:d}" />',
        )

        response = self.client.get(
            f"/admin/reversion_compare_tests/person/{self.person.pk}/history/compare/",
            data={"version_id2": version_ids[0], "version_id1": version_ids[1]},
        )
        # debug_response(response) # from django-tools

        self.assertContainsHtml(
            response,
            """
            <p><pre class="highlight">
            <del>- Dave</del>
            <ins>+ David</ins>
            </pre></p>
            """,
            "<blockquote>version 3: change the name</blockquote>",  # edit comment
        )
        self.assertNotContainsHtml(response, "pet", 'class="follow"')  # All fields are under reversion control
