#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.IntegerField()

    :copyleft: 2012-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from reversion.models import Version

from .utils.fixtures import Fixtures
from .utils.test_cases import BaseTestCase


class OneToOneFieldTest(BaseTestCase):
    "Test a model which uses a custom reversion manager."

    def setUp(self):
        super(OneToOneFieldTest, self).setUp()
        fixtures = Fixtures(verbose=False)
        self.person, self.item = fixtures.create_PersonIdentity_data()

        queryset = Version.objects.get_for_object(self.person)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_select_compare(self):
        response = self.client.get(f"/admin/reversion_compare_tests/person/{self.person.pk}/history/")

        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{self.version_ids[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{self.version_ids[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids[1]:d}" />',
        )

    def test_compare(self):
        response = self.client.get(
            f"/admin/reversion_compare_tests/person/{self.person.pk}/history/compare/",
            data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]},
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
