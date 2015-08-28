# coding: utf-8

"""
    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import os

from django.core.management import call_command, BaseCommand
from tests.test_utils.test_data import TestData


class Command(BaseCommand):
    help = 'Run Unittest-Server'
    def handle(self, *args, **options):
        """
        INFO: The django reloader will call this multiple times!
        We check RUN_MAIN, that will be set in django.utils.autoreload
        So we can skip the first migrate run.
        """
        self.stdout.write("\n")
        if os.environ.get("RUN_MAIN"):
            print("\n *** call 'migrate' command:")
            call_command("migrate", interactive=False, verbosity=1)

            # insert all unittest data into database:
            TestData(verbose=True).create_all()

        print("\n *** call 'runserver' command:")
        call_command("runserver",
             use_threading=False,
             use_reloader=True  ,
             verbosity=2
        )
