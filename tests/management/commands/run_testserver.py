# coding: utf-8

"""
    :copyleft: 2015-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import os

from django.core.management import call_command, BaseCommand
from tests.test_utils.test_data import TestData


class Command(BaseCommand):
    help = 'Run Unittest-Server'

    def verbose_call(self, command, **kwargs):
        self.stdout.write("\n")
        self.stdout.write("_"*79)
        self.stdout.write(self.style.NOTICE(
            " *** call '%s' command:" % command
        ))
        self.stdout.write("\n")
        call_command(command, **kwargs)

    def handle(self, *args, **options):
        """
        INFO: The django reloader will call this multiple times!
        We check RUN_MAIN, that will be set in django.utils.autoreload
        So we can skip the first migrate run.
        """
        if os.environ.get("RUN_MAIN"):
            self.verbose_call("diffsettings")#, interactive=False, verbosity=1)

            self.verbose_call("migrate", interactive=False, verbosity=1)

            # insert all unittest data into database:
            TestData(verbose=True).create_all()

        self.verbose_call("runserver",
             use_threading=False,
             use_reloader=True  ,
             verbosity=2
        )
