# coding: utf-8

"""
    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.core.management import call_command, BaseCommand
from tests.test_utils.test_data import TestData


class Command(BaseCommand):
    help = 'Run Unittest-Server'
    def handle(self, *args, **options):
        print("\ncall 'migrate' command:")
        call_command("migrate", interactive=False, verbosity=1)

        TestData(verbose=True).create_all()

        print("\n call 'runserver' command:")
        # IMPORTANT is use_reloader=False: The reloader will call this multiple times!
        call_command("runserver", use_threading=False, use_reloader=False, verbosity=2)
