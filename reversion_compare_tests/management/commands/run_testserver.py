"""
    :copyleft: 2015-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os
from pathlib import Path

from bx_py_utils.path import assert_is_dir
from django.core.management import BaseCommand, call_command

import reversion_compare_tests
from reversion_compare_tests.utils.fixtures import Fixtures


BASE_PATH = Path(reversion_compare_tests.__file__).parent


class Command(BaseCommand):
    help = "Run Unittest-Server"

    def verbose_call(self, command, **kwargs):
        self.stdout.write("\n")
        self.stdout.write("_" * 79)
        self.stdout.write(self.style.NOTICE(f" *** call '{command}' command:"))
        self.stdout.write("\n")
        call_command(command, **kwargs)

    def handle(self, *args, **options):
        """
        INFO: The django reloader will call this multiple times!
        We check RUN_MAIN, that will be set in django.utils.autoreload
        So we can skip the first migrate run.
        """
        if os.environ.get("RUN_MAIN"):
            self.verbose_call("diffsettings")  # , interactive=False, verbosity=1)

            self.clean_migration_files()

            self.verbose_call("makemigrations", interactive=False, verbosity=1)
            self.verbose_call("migrate", run_syncdb=True, interactive=False, verbosity=1)
            self.verbose_call("showmigrations", verbosity=1)

            # insert all unittest data into database:
            Fixtures(verbose=True).create_all()

        self.verbose_call("runserver", use_threading=True, use_reloader=True, verbosity=2)

    def clean_migration_files(self):
        migration_path = BASE_PATH / 'migrations'
        assert_is_dir(migration_path)
        for item in migration_path.glob('*.py'):
            if item.name.startswith('_'):
                continue
            self.stdout.write(self.style.NOTICE(f'Remove migration {item}'))
            item.unlink(missing_ok=True)
