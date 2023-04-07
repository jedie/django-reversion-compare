import logging
from pathlib import Path

from debug_toolbar.middleware import show_toolbar
from django.conf import settings


logger = logging.getLogger(__name__)


def djdt_show(request):
    """
    Determining whether the Django Debug Toolbar should show or not.
    """
    if not settings.DEBUG:
        return False

    if Path('/.dockerenv').exists():
        # We run in a docker container
        # skip the `request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS` check.
        return True

    return show_toolbar(request)
