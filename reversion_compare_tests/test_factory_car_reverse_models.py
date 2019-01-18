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

from __future__ import absolute_import, division, print_function

from django.db import connection
from django.test.utils import CaptureQueriesContext

from reversion import is_registered, revisions, unregister
from reversion.models import Revision, Version

from .models import Car, Factory, Person
from .utils.db_queries import print_db_queries
from .utils.test_cases import BaseTestCase
from .utils.fixtures import Fixtures

try:
    import django_tools
except ImportError as err:
    msg = (
        "Please install django-tools for unittests" " - https://github.com/jedie/django-tools/" " - Original error: %s"
    ) % err
    raise ImportError(msg)


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
        super(FactoryCarReverseRelationModelTest, self).setUp()

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
        response = self.client.get("/admin/reversion_compare_tests/factory/%s/history/" % self.factory.pk)
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
        )

    def assert_diff1(self, response):
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            """
            <p class="highlight">
                <del>- motor-car three from factory one supplier(s):</del> &rarr; Deleted<br />
                <ins>+ motor-car four from factory one supplier(s): </ins><br />
                motor-car one from factory one supplier(s): <br />
            </p>
            """,
            """
            <p class="highlight">
                <ins>+ Bob Bobertson</ins><br />
            </p>
            """,
            "<blockquote>version 2: discontinued car-three, add car-four, add Bob the worker</blockquote>",  # edit comment
        )

    def test_diff1(self):
        response = self.client.get(
            "/admin/reversion_compare_tests/factory/%s/history/compare/" % self.factory.pk,
            data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]},
        )
        self.assert_diff1(response)

    def test_select_compare1_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/admin/reversion_compare_tests/factory/%s/history/compare/" % self.factory.pk,
                data={"version_id2": self.version_ids[1], "version_id1": self.version_ids[2]},
            )
            self.assert_diff1(response)

        # print_db_queries(queries.captured_queries)
        # total queries....: 37
        # unique queries...: 28
        # duplicate queries: 9

        self.assertLess(len(queries.captured_queries), 37 + 2)  # real+buffer
