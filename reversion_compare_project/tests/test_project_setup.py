from pathlib import Path
from unittest import TestCase

from bx_py_utils.path import assert_is_dir
from cli_base.cli_tools.code_style import assert_code_style
from django.conf import settings
from django.core.cache import cache
from manage_django_project.config import project_info
from manage_django_project.test_utilities import CallManagePy
from manageprojects.test_utils.project_setup import check_editor_config, get_py_max_line_length
from packaging.version import Version

import reversion_compare


class ProjectSetupTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        project_info.assert_initialized()
        project_root_path = project_info.config.project_root_path
        cls.call_manage_py = CallManagePy(project_root=project_root_path)

    def test_project_path(self):
        project_path = settings.BASE_PATH
        assert_is_dir(project_path)
        assert_is_dir(project_path / 'reversion_compare')
        assert_is_dir(project_path / 'reversion_compare_project')

    def test_template_dirs(self):
        assert len(settings.TEMPLATES) == 1
        dirs = settings.TEMPLATES[0].get('DIRS')
        assert len(dirs) == 1
        template_path = Path(dirs[0]).resolve()
        assert template_path.is_dir()

    def test_cache(self):
        # django cache should work in tests, because some tests "depends" on it
        cache_key = 'a-cache-key'
        self.assertIs(cache.get(cache_key), None)
        cache.set(cache_key, 'the cache content', timeout=1)
        self.assertEqual(cache.get(cache_key), 'the cache content', f'Check: {settings.CACHES=}')
        cache.delete(cache_key)
        self.assertIs(cache.get(cache_key), None)

    def test_settings(self):
        self.assertEqual(settings.SETTINGS_MODULE, 'reversion_compare_project.settings.tests')
        middlewares = [entry.rsplit('.', 1)[-1] for entry in settings.MIDDLEWARE]
        assert 'AlwaysLoggedInAsSuperUserMiddleware' not in middlewares
        assert 'DebugToolbarMiddleware' not in middlewares

    def test_version(self):
        self.assertIsNotNone(reversion_compare.__version__)

        version = Version(reversion_compare.__version__)  # Will raise InvalidVersion() if wrong formatted
        self.assertEqual(str(version), reversion_compare.__version__)

        output = self.call_manage_py.verbose_check_output('version')
        self.assertIn(reversion_compare.__version__, output)

    def test_manage(self):
        output = self.call_manage_py.verbose_check_output('project_info')
        self.assertIn('reversion_compare_project', output)
        self.assertIn('reversion_compare_project.settings.local', output)
        self.assertIn('reversion_compare_project.settings.tests', output)
        self.assertIn(reversion_compare.__version__, output)

        output = self.call_manage_py.verbose_check_output('check')
        self.assertIn('System check identified no issues (0 silenced).', output)

        output = self.call_manage_py.verbose_check_output('makemigrations')
        self.assertIn('No changes detected', output)

    def test_code_style(self):
        return_code = assert_code_style(package_root=settings.BASE_PATH)
        self.assertEqual(return_code, 0, 'Code style error, see output above!')

    def test_check_editor_config(self):
        check_editor_config(package_root=settings.BASE_PATH)

        max_line_length = get_py_max_line_length(package_root=settings.BASE_PATH)
        self.assertEqual(max_line_length, 119)
