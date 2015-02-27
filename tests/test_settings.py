
import os
import tempfile

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
)
MIDDLEWARE_CLASSES = ()

# LANGUAGE_CODE = "en"
# LANGUAGES = (
#     ("en","en"),
# )
SECRET_KEY = 'unittests-fake-key'

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    'reversion',

    'reversion_compare',
    'tests',
]

TEMP_DIR = tempfile.mkdtemp(prefix="reversion_compare_unittest_")
print("Use temp dir: %r" % TEMP_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEMP_DIR, 'cmsplugin_markup_unittest_database'),
    }
}
