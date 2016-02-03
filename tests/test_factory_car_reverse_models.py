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

from __future__ import absolute_import, division, print_function


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

from reversion_compare import reversion_api

from .models import Factory, Car, Person
from .test_utils.test_cases import BaseTestCase
from .test_utils.test_data import TestData

class FactoryCarReverseRelationModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car

    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """
    def setUp(self):
        reversion_api.unregister(Person)
        reversion_api.unregister(Car)
        reversion_api.unregister(Factory)
        reversion_api.register(Factory, follow=["building_ptr","cars","workers"])
        reversion_api.register(Car)
        reversion_api.register(Person, follow=["pets"])
        super(FactoryCarReverseRelationModelTest, self).setUp()

        test_data = TestData(verbose=False)
        self.factory = test_data.create_Factory_reverse_relation_data()
        queryset = reversion_api.get_for_object(self.factory)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion_api.is_registered(Factory))
        self.assertTrue(reversion_api.is_registered(Car))
        self.assertEqual(reversion_api.Revision.objects.all().count(), 3)
        self.assertEqual(len(self.version_ids), 3)
        self.assertEqual(reversion_api.Version.objects.all().count(), 19)

    def test_select_compare(self):
        response = self.client.get("/admin/tests/factory/%s/history/" % self.factory.pk)
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
            "/admin/tests/factory/%s/history/compare/" % self.factory.pk,
            data={"version_id2":self.version_ids[2], "version_id1":self.version_ids[1]}
        )
        #debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '''
            <p class="highlight">
                <del>- motor-car three from factory one supplier(s):</del> &rarr; Deleted<br />
                <ins>+ motor-car four from factory one supplier(s): </ins><br />
                motor-car one from factory one supplier(s): <br />
            </p>
            ''',
            '''
            <p class="highlight">
                <ins>+ Bob Bobertson</ins><br />
            </p>
            ''',
            '<blockquote>version 2: discontinued car-three, add car-four, add Bob the worker</blockquote>', # edit comment
        )

