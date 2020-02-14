#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test history compare CBV

    :copyleft: 2012-2017 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import connection
from django.test.utils import CaptureQueriesContext
from reversion import is_registered
from reversion.models import Version

from .models import SimpleModel
from .utils.fixtures import Fixtures
from .utils.test_cases import BaseTestCase


class CBViewTest(BaseTestCase):
    """
    unittests for testing reversion_compare.views.HistoryCompareDetailView

    Tests for the basic functions.
    """

    def setUp(self):
        super(CBViewTest, self).setUp()
        fixtures = Fixtures(verbose=False)
        self.item1, self.item2 = fixtures.create_Simple_data()

        queryset = Version.objects.get_for_object(self.item1)
        self.version_ids1 = queryset.values_list("pk", flat=True)

        queryset = Version.objects.get_for_object(self.item2)
        self.version_ids2 = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(is_registered(SimpleModel))

        self.assertEqual(SimpleModel.objects.count(), 2)
        self.assertEqual(SimpleModel.objects.all()[0].text, "version two")

        self.assertEqual(Version.objects.get_for_object(self.item1).count(), 2)
        self.assertEqual(list(self.version_ids1), [2, 1])

        self.assertEqual(list(self.version_ids1), [2, 1])
        self.assertEqual(list(self.version_ids2), [7, 6, 5, 4, 3])

    def assert_select_compare1(self, response):
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{self.version_ids1[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids1[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{self.version_ids1[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids1[1]:d}" />',
        )

    def test_select_compare1(self):
        response = self.client.get(f"/test_view/{self.item1.pk}")
        self.assert_select_compare1(response)

    def test_select_compare1_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/test_view/{self.item1.pk}")
            self.assert_select_compare1(response)

        # print_db_queries(queries.captured_queries)
        # total queries....: 7
        # unique queries...: 4
        # duplicate queries: 3

        self.assertLess(len(queries.captured_queries), 7 + 2)  # real+buffer

    def test_select_compare2(self):
        response = self.client.get(f"/test_view/{self.item2.pk}")
        for i in range(4):
            if i == 0:
                comment = f"create v{i:d}"
            else:
                comment = f"change to v{i:d}"

            self.assertContainsHtml(response, f"<td>{comment}</td>", '<input type="submit" value="compare">')

    def assert_select_compare_and_diff(self, response):
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{self.version_ids1[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids1[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{self.version_ids1[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids1[1]:d}" />',
        )
        self.assertContainsHtml(
            response,
            "<del>- version one</del>",
            "<ins>+ version two</ins>",
            "<blockquote>simply change the CharField text.</blockquote>",  # edit comment
        )

    def test_select_compare_and_diff(self):
        response = self.client.get(
            f"/test_view/{self.item1.pk}",
            data={"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]},
        )
        self.assert_select_compare_and_diff(response)

    def test_select_compare_and_diff_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                f"/test_view/{self.item1.pk}",
                data={"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]},
            )
            self.assert_select_compare_and_diff(response)

        # print_db_queries(queries.captured_queries)
        # total queries....: 15
        # unique queries...: 9
        # duplicate queries: 6
        self.assertLess(len(queries.captured_queries), 15 + 2)  # real+buffer

    def test_prev_next_buttons(self):
        base_url = f"/test_view/{self.item2.pk}"
        for i in range(4):
            # IDs: 3,4,5,6
            id1 = i + 3
            id2 = i + 4
            response = self.client.get(base_url, data={"version_id2": id2, "version_id1": id1})
            self.assertContainsHtml(
                response,
                f"<del>- v{i:d}</del>",
                "<ins>+ v%i</ins>" % (i + 1),
                "<blockquote>change to v%i</blockquote>" % (i + 1),
            )

            next = '<a href="?version_id1=%s&amp;version_id2=%s">next &rsaquo;</a>' % (i + 4, i + 5)
            prev = '<a href="?version_id1=%s&amp;version_id2=%s">&lsaquo; previous</a>' % (i + 2, i + 3)

            if i == 0:
                self.assertNotContains(response, "previous")
                self.assertContains(response, "next")
                self.assertContainsHtml(response, next)
            elif i == 3:
                self.assertContains(response, "previous")
                self.assertNotContains(response, "next")
                self.assertContainsHtml(response, prev)
            else:
                self.assertContains(response, "previous")
                self.assertContains(response, "next")
                self.assertContainsHtml(response, prev, next)
