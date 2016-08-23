#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.IntegerField()

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
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

from reversion_compare import reversion_api
from .test_utils.test_cases import BaseTestCase
from .test_utils.test_data import TestData


class OneToOneFieldTest(BaseTestCase):
    "Test a model which uses a custom reversion manager."

    def setUp(self):
        super(OneToOneFieldTest, self).setUp()
        test_data = TestData(verbose=False)
        self.person, self.item = test_data.create_PersonIdentity_data()

        queryset = reversion_api.get_for_object(self.person)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_select_compare(self):
        response = self.client.get("/admin/tests/person/%s/history/" % self.person.pk)

        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
        )

    def test_compare(self):
        response = self.client.get(
            "/admin/tests/person/%s/history/compare/" % self.person.pk,
            data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]}
        )

        self.assertContainsHtml(
            response,
            """
            <pre class="highlight">
                <del>- Dave</del>
                <ins>+ John</ins>
            </pre>
            """,
            "<blockquote>version 2: change person name.</blockquote>",
        )
