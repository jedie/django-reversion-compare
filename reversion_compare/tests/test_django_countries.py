#!/usr/bin/env python

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2022 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from reversion.models import Version

from reversion_compare_project.utils.fixtures import Fixtures
from reversion_compare_project.utils.test_cases import BaseTestCase


class CountryFieldTestModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        # fixtures = Fixtures(verbose=False)
        fixtures = Fixtures(verbose=True)
        self.instance = fixtures.create_CountryFieldTestModel_data()

        queryset = Version.objects.get_for_object(self.instance)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_diff(self):
        response = self.client.get(
            f"/en/admin/reversion_compare_project/countryfieldtestmodel/{self.instance.pk}/history/compare/",
            data={"version_id2": self.version_ids[0], "version_id1": self.version_ids[1]},
        )
        self.assertEqual(response.status_code, 200, response)
        self.assertTemplateUsed(response, 'reversion-compare/compare.html')
        self.assert_html_parts(
            response,
            parts=(
                "<h3>one country</h3>",
                """
                <div class="module">
                    <pre class="highlight"><del>- Germany</del>
                    <ins>+ United Kingdom</ins></pre>
                </div>
                """,
                "<h3>multiple countries</h3>",
                # TODO: Enhance Django-Countries diff:
                """
                <span class="diff-line diff-del diff-ins">
                [&#x27;Austria&#x27;, &#x27;<del>Germany</del>
                <ins>Switzerland&#x27;, &#x27;Germany&#x27;, &#x27;United Kingdom</ins>&#x27;]
                </span>
                """,
            ),
        )
