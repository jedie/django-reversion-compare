"""
    :copyleft: 2015-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

from django_tools.management.commands.run_testserver import Command as RunServerCommand

import reversion_compare_project
from reversion_compare_project.utils.fixtures import Fixtures


BASE_PATH = Path(reversion_compare_project.__file__).parent


class Command(RunServerCommand):
    def post_setup(self, **options) -> None:
        # insert all unittest data into database:
        Fixtures(verbose=True).create_all()
