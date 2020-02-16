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


import unittest

from reversion.models import Version
from reversion_compare import helpers

from .utils.fixtures import Fixtures
from .utils.test_cases import BaseTestCase


class TemplateFieldModelTest(BaseTestCase):
    """
    unittests that used reversion_compare_test_app.models.SimpleModel

    Tests for the basic functions.
    """

    def setUp(self):
        super().setUp()
        fixtures = Fixtures(verbose=False)
        self.item1, self.item2 = fixtures.create_TemplateField_data()

        queryset = Version.objects.get_for_object(self.item1)
        self.version_ids1 = queryset.values_list("pk", flat=True)

        queryset = Version.objects.get_for_object(self.item2)
        self.version_ids2 = queryset.values_list("pk", flat=True)

    def test_diff(self):
        response = self.client.get(
            f"/admin/reversion_compare_tests/templatefield/{self.item1.pk}/history/compare/",
            data={"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]},
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            "<del>- version one</del>",
            "<ins>+ version two</ins>",
            "<blockquote>simply change the CharField text.</blockquote>",  # edit comment
        )

    @unittest.skipIf(not hasattr(helpers, "diff_match_patch"), "No google-diff-match-patch available")
    def test_google_diff_match_patch(self):
        self.activate_google_diff_match_patch()
        response = self.client.get(
            f"/admin/reversion_compare_tests/templatefield/{self.item1.pk}/history/compare/",
            data={"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]},
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            """
            <p><span>version </span>
            <del style="background:#ffe6e6;">one</del>
            <ins style="background:#e6ffe6;">two</ins>
            </p>
            """,
            "<blockquote>simply change the CharField text.</blockquote>",  # edit comment
        )
