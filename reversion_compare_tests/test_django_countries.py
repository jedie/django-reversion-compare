#!/usr/bin/env python

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2022 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from reversion.models import Version

from reversion_compare_tests.utils.fixtures import Fixtures
from reversion_compare_tests.utils.test_cases import BaseTestCase


class CountryFieldTestModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        fixtures = Fixtures(verbose=False)
        # fixtures = Fixtures(verbose=True)
        self.instance = fixtures.create_CountryFieldTestModel_data()

        queryset = Version.objects.get_for_object(self.instance)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_diff(self):
        response = self.client.get(
            f"/admin/reversion_compare_tests/countryfieldtestmodel/{self.instance.pk}/history/compare/",
            data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]},
        )
