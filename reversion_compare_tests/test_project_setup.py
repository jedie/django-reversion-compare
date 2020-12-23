"""
    :copyleft: 2020 by revision-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

from creole.setup_utils import update_rst_readme
from poetry_publish.tests.test_project_setup import test_poetry_check as assert_poetry_check
from poetry_publish.tests.test_project_setup import test_version as assert_version

import reversion_compare
from reversion_compare import __version__


PACKAGE_ROOT = Path(reversion_compare.__file__).parent.parent


def test_version():
    """
    Check if current version exists in README
    Check if current version is in pyproject.toml
    """
    assert_version(package_root=PACKAGE_ROOT, version=__version__)


def test_update_rst_readme(capsys):
    rest_readme_path = update_rst_readme(
        package_root=PACKAGE_ROOT, filename='README.creole'
    )
    captured = capsys.readouterr()
    assert captured.out == 'Generate README.rst from README.creole...nothing changed, ok.\n'
    assert captured.err == ''
    assert isinstance(rest_readme_path, Path)
    assert str(rest_readme_path).endswith('/README.rst')


def test_poetry_check():
    """
    Test 'poetry check' output.
    """
    assert_poetry_check(package_root=PACKAGE_ROOT)
