import logging

from reversion.models import Version

from reversion_compare_project.utils.fixtures import Fixtures
from reversion_compare_project.utils.test_cases import BaseTestCase


class MigrationModelTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        fixtures = Fixtures(verbose=False)
        cls.instance = fixtures.create_MigrationModel_data()

        queryset = Version.objects.get_for_object(cls.instance)
        cls.version_ids = list(queryset.values_list("pk", flat=True))

    def test_compare_raw(self):
        assert self.version_ids == [4, 3, 2, 1]
        assert self.instance.pk == 1

        response = self.client.get('/en/admin/reversion_compare_project/migrationmodel/1/history/')
        self.assertEqual(response.status_code, 200, response)
        self.assertTemplateUsed(response, 'reversion-compare/object_history.html')
        self.assert_html_parts(
            response,
            parts=(
                '<input type="submit" value="compare">',
                '<td>Migration state 2 - version 4</td>',
                '<td>Migration state 2 - version 3</td>',
                '<td>Migration state 1 - version 2</td>',
                '<td>Migration state 1 - version 1</td>',
            ),
        )

        with self.assertLogs('reversion_compare', level=logging.WARNING) as logs:
            response = self.client.get(
                '/en/admin/reversion_compare_project/migrationmodel/1/history/compare/',
                data={'version_id2': 3, 'version_id1': 2},
            )
            self.assertEqual(response.status_code, 200, response)
            self.assertTemplateUsed(response, 'reversion-compare/compare_raw.html')
            self.assert_html_parts(
                response,
                parts=(
                    '<blockquote>Migration state 2 - version 3</blockquote>',
                    '<del>2</del>',
                    '<ins>3</ins>',
                    'Not a number 2',
                    'Lorem ipsum dolor sit amet,',
                    'Revert to the old version will probably not work!',
                ),
            )
        error_msg = logs.output[0]
        assert 'Fallback compare caused by:' in error_msg
        assert 'incompatible version data' in error_msg
