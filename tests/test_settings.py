
import os
import tempfile

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    "reversion.middleware.RevisionMiddleware",
    
    #'django_tools.middlewares.QueryLogMiddleware.QueryLogMiddleware',
)

LANGUAGE_CODE = "en"
LANGUAGES = (
    ("en","de"),
)
SECRET_KEY = 'unittests-fake-key'

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sessions',

    'reversion',

    'reversion_compare',
    'tests',
]

ROOT_URLCONF="tests.urls"
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

UNITTEST_TEMP_PATH = tempfile.mkdtemp(prefix="reversion_compare_unittest_")
print("Use temp dir: %r" % UNITTEST_TEMP_PATH)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(UNITTEST_TEMP_PATH, 'cmsplugin_markup_unittest_database'),
    }
}

DEBUG=True

# add reversion models to django admin:
ADD_REVERSION_ADMIN=True