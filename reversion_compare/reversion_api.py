import reversion
from reversion.models import Revision, Version

if reversion.__version__ > (2, 0):
    from reversion import revisions as reversion
    from reversion.revisions import (
        register, unregister, is_registered,
        get_registered_models,
        create_revision, set_comment, _get_options
    )
    get_for_object_reference = Version.objects.get_for_object_reference
    get_for_object = Version.objects.get_for_object
    get_deleted = Version.objects.get_deleted
elif reversion.__version__ > (1, 10):
    from reversion import revisions as reversion
    from reversion.revisions import (
        register, unregister, is_registered,
        get_for_object, get_for_object_reference, get_registered_models, get_deleted,
        create_revision, set_comment, default_revision_manager
    )
    _get_options = default_revision_manager.get_adapter
else:
    # django-reversion <= 1.9
    from reversion import (
        register, unregister, is_registered,
        get_for_object, get_for_object_reference, get_registered_models, get_deleted,
        create_revision, set_comment, default_revision_manager
    )
    _get_options = default_revision_manager.get_adapter

