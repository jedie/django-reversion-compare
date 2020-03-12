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


from django.db import connection
from django.test.utils import CaptureQueriesContext

from reversion import is_registered, revisions, unregister
from reversion.models import Revision, Version

from .models import Car, Factory, Person
from .utils.fixtures import Fixtures
from .utils.test_cases import BaseTestCase


class FactoryCarReverseRelationModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car

    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """

    def setUp(self):
        unregister(Person)
        unregister(Car)
        unregister(Factory)
        revisions.register(Factory, follow=["building_ptr", "cars", "workers"])
        revisions.register(Car)
        revisions.register(Person, follow=["pets"])
        super().setUp()

        fixtures = Fixtures(verbose=False)
        self.factory = fixtures.create_Factory_reverse_relation_data()
        queryset = Version.objects.get_for_object(self.factory)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(is_registered(Factory))
        self.assertTrue(is_registered(Car))
        self.assertTrue(is_registered(Person))
        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(len(self.version_ids), 3)
        self.assertEqual(Version.objects.all().count(), 19)

    def test_select_compare(self):
        response = self.client.get(f"/admin/reversion_compare_tests/factory/{self.factory.pk}/history/")
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{self.version_ids[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{self.version_ids[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[1]:d}" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[2]:d}" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[2]:d}" />',
        )

    def assert_diff1(self, response):
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            """
            <p class="highlight">
                <ins>+ Bob Bobertson</ins><br />
            </p>
            """,
            """
            <div class="module">
                <p class="highlight">
                    <del>- motor-car three from factory one supplier(s): </del>  &rarr; Deleted<br />
                    <ins>+ motor-car four from factory one supplier(s): </ins><br />
                    motor-car one from factory one supplier(s): <br />
                </p>
            </div>
            """,
            # edit comment:
            "<blockquote>version 2: discontinued car-three, add car-four, add Bob the worker</blockquote>",
        )

    def test_diff1(self):
        response = self.client.get(
            f"/admin/reversion_compare_tests/factory/{self.factory.pk}/history/compare/",
            data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]},
        )
        self.assert_diff1(response)

    def test_select_compare1_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                f"/admin/reversion_compare_tests/factory/{self.factory.pk}/history/compare/",
                data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]},
            )
            self.assert_diff1(response)

        # print_db_queries(queries.captured_queries)
        # total queries....: 37
        # unique queries...: 28
        # duplicate queries: 9

        self.assertLess(len(queries.captured_queries), 37 + 2)  # real+buffer
