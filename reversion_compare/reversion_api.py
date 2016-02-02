
import reversion
if reversion.__version__ > (1,10):
    from reversion import revisions as reversion
    from reversion.revisions import (
        register, unregister, is_registered,
        get_for_object, get_registered_models, get_deleted,
        create_revision, set_comment
    )
else:
    # django-reversion <= 1.9
    from reversion import (
        register, unregister, is_registered,
        get_for_object, get_registered_models, get_deleted,
        create_revision, set_comment
    )


from reversion.models import Revision, Version, has_int_pk