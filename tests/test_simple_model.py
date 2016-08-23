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

from reversion_compare import reversion_api, helpers
from .test_utils.test_cases import BaseTestCase
from .models import SimpleModel
from .test_utils.test_data import TestData


class SimpleModelTest(BaseTestCase):
    """
    unittests that used reversion_compare_test_app.models.SimpleModel

    Tests for the basic functions.
    """
    def setUp(self):
        super(SimpleModelTest, self).setUp()
        test_data = TestData(verbose=False)
        # test_data = TestData(verbose=True)
        self.item1, self.item2 = test_data.create_Simple_data()

        queryset = reversion_api.get_for_object(self.item1)
        self.version_ids1 = queryset.values_list("pk", flat=True)

        queryset = reversion_api.get_for_object(self.item2)
        self.version_ids2 = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion_api.is_registered(SimpleModel))

        self.assertEqual(SimpleModel.objects.count(), 2)
        self.assertEqual(SimpleModel.objects.all()[0].text, "version two")

        self.assertEqual(reversion_api.get_for_object(self.item1).count(), 2)
        self.assertEqual(reversion_api.get_for_object(self.item2).count(), 5)
        self.assertEqual(reversion_api.Revision.objects.all().count(), 7)
        self.assertEqual(reversion_api.Version.objects.all().count(), 7)

        # query.ValuesListQuerySet() -> list():
        self.assertEqual(list(self.version_ids1), [2, 1])
        self.assertEqual(list(self.version_ids2), [7, 6, 5, 4, 3])

    def test_select_compare1(self):
        response = self.client.get("/admin/tests/simplemodel/%s/history/" % self.item1.pk)
        #  debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids1[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids1[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids1[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids1[1],
        )

    def test_select_compare2(self):
        response = self.client.get("/admin/tests/simplemodel/%s/history/" % self.item2.pk)
        # debug_response(response) # from django-tools
        for i in range(4):
            if i == 0:
                comment = "create v%i" % i
            else:
                comment = "change to v%i" % i

            self.assertContainsHtml(
                response,
                "<td>%s</td>" % comment,
                '<input type="submit" value="compare">',
            )

    def test_diff(self):
        response = self.client.get(
            "/admin/tests/simplemodel/%s/history/compare/" % self.item1.pk,
            data={"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        )
        # debug_response(response) # from django-tools
        self.assertContainsHtml(
            response,
            '<del>- version one</del>',
            '<ins>+ version two</ins>',
            '<blockquote>simply change the CharField text.</blockquote>',  # edit comment
        )

        if self.google_diff_match_patch:
            # google-diff-match-patch is available
            helpers.google_diff_match_patch = True
            try:
                self.assertContainsHtml(
                    response,
                    """
                    <p><span>version </span>
                    <del style="background:#ffe6e6;">one</del>
                    <ins style="background:#e6ffe6;">two</ins>
                    </p>
                    """,
                    '<blockquote>simply change the CharField text.</blockquote>',  # edit comment
                )
            finally:
                helpers.google_diff_match_patch = False # revert

    def test_prev_next_buttons(self):
        base_url = "/admin/tests/simplemodel/%s/history/compare/" % self.item2.pk
        for i in range(4):
            # IDs: 3,4,5,6
            id1 = i+3
            id2 = i+4
            response = self.client.get(
                base_url,
                data={"version_id2": id2, "version_id1": id1}
            )
            self.assertContainsHtml(
                response,
                '<del>- v%i</del>' % i,
                '<ins>+ v%i</ins>' % (i+1),
                '<blockquote>change to v%i</blockquote>' % (i+1),
            )
            # print("\n\n+++", i)
            # for line in response.content.decode("utf-8").split("\n"):
            #     if "next" in line or "previous" in line:
            #         print(line)
            """
            +++ 0
                <li><a href="?version_id1=4&amp;version_id2=5">next &rsaquo;</a></li>
            +++ 1
                <li><a href="?version_id1=3&amp;version_id2=4">&lsaquo; previous</a></li>
                <li><a href="?version_id1=5&amp;version_id2=6">next &rsaquo;</a></li>
            +++ 2
                <li><a href="?version_id1=4&amp;version_id2=5">&lsaquo; previous</a></li>
                <li><a href="?version_id1=6&amp;version_id2=7">next &rsaquo;</a></li>
            +++ 3
                <li><a href="?version_id1=5&amp;version_id2=6">&lsaquo; previous</a></li>
            """

            next = '<a href="?version_id1=%s&amp;version_id2=%s">next &rsaquo;</a>' % (i+4, i+5)
            prev = '<a href="?version_id1=%s&amp;version_id2=%s">&lsaquo; previous</a>' % (i+2, i+3)

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
