"""
    Helper to compare raw version data.
    see: https://github.com/etianen/django-reversion/issues/859

    :copyleft: 2021 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import json
import pprint

from django.core.serializers.json import DjangoJSONEncoder
from reversion.models import Version


def get_version_data(version):
    """
    Get field data from a Version instance.
    """
    assert isinstance(version, Version)
    assert version.format == 'json', f'{version.format!r} not supported (only JSON)'

    json_string = version.serialized_data
    version_data = json.loads(json_string)
    # version_data looks like:
    # [{'fields': {'info': 'Migration state 2 - version 4',
    #              'number_then_text': 111,
    #              'text': 'Now this is a short text!!!'},
    #   'model': 'reversion_compare_project.migrationmodel',
    #   'pk': 1}]
    assert len(version_data) == 1
    fields_data = version_data[0]['fields']
    return fields_data


def pformat(value):
    try:
        return DjangoJSONEncoder(indent=4, sort_keys=True, ensure_ascii=False).encode(value)
    except TypeError:
        # Fallback if values are not serializable with JSON:
        return pprint.pformat(value, width=120)
