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


from django.urls import reverse
from reversion import create_revision
from reversion.models import Revision, Version

from reversion_compare_project.models import CustomModel
from reversion_compare_project.utils.fixtures import Fixtures
from reversion_compare_project.utils.test_cases import BaseTestCase


class CustomModelTest(BaseTestCase):
    """Test a model which uses a custom reversion manager."""

    def setUp(self):
        super().setUp()
        fixtures = Fixtures(verbose=False)
        self.item = fixtures.create_CustomModel_data()

    def test_initial_state(self):
        """ "Test initial data creation and model registration."""
        self.assertEqual(CustomModel.objects.count(), 1)
        self.assertEqual(Version.objects.get_for_object(self.item).count(), 1)
        self.assertEqual(Revision.objects.all().count(), 1)

    def test_text_diff(self):
        """ "Generate a new revision and check for a correctly generated diff."""
        with create_revision():
            self.item.text = "version two"
            self.item.save()
        queryset = Version.objects.get_for_object(self.item)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 2)
        url_name = f"admin:{CustomModel._meta.app_label}_{CustomModel._meta.model_name}_compare"
        diff_url = reverse(url_name, args=(self.item.pk,))
        data = {"version_id2": version_ids[0], "version_id1": version_ids[1]}
        response = self.client.get(diff_url, data=data)
        self.assertContains(response, "<del>- version one</del>")
        self.assertContains(response, "<ins>+ version two</ins>")

    def test_version_selection(self):
        """Generate two revisions and view the version history selection."""
        with create_revision():
            self.item.text = "version two"
            self.item.save()
        with create_revision():
            self.item.text = "version three"
            self.item.save()
        queryset = Version.objects.get_for_object(self.item)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)
        url_name = f"admin:{CustomModel._meta.app_label}_{CustomModel._meta.model_name}_history"
        history_url = reverse(url_name, args=(self.item.pk,))
        response = self.client.get(history_url)
        self.assertContainsHtml(
            response,
            '<input type="submit" value="compare">',
            f'<input type="radio" name="version_id1" value="{version_ids[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{version_ids[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{version_ids[1]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{version_ids[1]:d}" />',
            f'<input type="radio" name="version_id1" value="{version_ids[2]:d}" />',
            f'<input type="radio" name="version_id2" value="{version_ids[2]:d}" />',
        )
