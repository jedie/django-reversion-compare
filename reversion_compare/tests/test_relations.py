import logging

from reversion.models import Version

from reversion_compare_project.utils.fixtures import Fixtures
from reversion_compare_project.utils.test_cases import BaseTestCase


class RelationTestCase(BaseTestCase):
    def test_non_registered_relation(self):
        instance = Fixtures(verbose=False).create_RegisteredWithNotRegisteredRelationModel_data()

        self.assertEqual(
            list(Version.objects.values('pk', 'revision__comment')),
            [
                {'pk': 2, 'revision__comment': 'Change'},
                {'pk': 1, 'revision__comment': 'init'},
            ],
        )
        with self.assertLogs('reversion_compare', level=logging.INFO) as logs:
            response = self.client.get(
                path=(
                    '/en/admin/reversion_compare_project'
                    f'/registeredwithnotregisteredrelationmodel/{instance.pk}/history/compare/'
                ),
                data={'version_id2': 2, 'version_id1': 1},
            )
            self.assertEqual(response.status_code, 200, response)
            self.assertTemplateUsed(response, 'reversion-compare/compare.html')
        self.assertEqual(
            logs.output,
            [
                (
                    'INFO:reversion_compare.compare:'
                    'Related model NotRegisteredModel has not been registered with django-reversion'
                ),
                (
                    'INFO:reversion_compare.compare:'
                    'Related model NotRegisteredModel has not been registered with django-reversion'
                ),
            ],
        )
        self.assert_html_parts(
            response,
            parts=(
                '<del>- Bar 1</del>',
                '<ins>+ Bar 2</ins>',
            ),
        )
