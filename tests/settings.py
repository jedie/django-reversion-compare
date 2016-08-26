
import os
import tempfile

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
        ],
    },
},]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    "reversion.middleware.RevisionMiddleware",
)

LANGUAGE_CODE = "en"
LANGUAGES = (
    ("en","de"),
)
SECRET_KEY = 'unittests-fake-key'

PASSWORD_HASHERS = [ # Speeding up the tests
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

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

try:
    UNITTEST_TEMP_PATH = os.environ["UNITTEST_TEMP_PATH"]
except KeyError:
    UNITTEST_TEMP_PATH = tempfile.mkdtemp(prefix="reversion_compare_unittest_")
    print("Use temp dir: %r" % UNITTEST_TEMP_PATH)
    os.environ["UNITTEST_TEMP_PATH"] = UNITTEST_TEMP_PATH

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(UNITTEST_TEMP_PATH, 'reversion_compare_unittest_database'),
    }
}

DEBUG = True

# add reversion models to django admin:
ADD_REVERSION_ADMIN = True