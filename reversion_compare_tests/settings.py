from pathlib import Path


print("Use settings:", __file__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(Path(BASE_DIR, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


MIDDLEWARE = (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    # WARNING:
    # This will 'disable' the authentication, because
    # the default user will always be logged in.
    "reversion_compare_tests.middleware.AlwaysLoggedInAsSuperUser",

    "django.contrib.messages.middleware.MessageMiddleware",

    "reversion.middleware.RevisionMiddleware",
)

# Username/password for reversion_compare_tests.middleware.AlwaysLoggedInAsSuperUser:
DEFAULT_USERNAME = "AutoLoginUser"
DEFAULT_USERPASS = "no password needed!"

SECRET_KEY = "unittests-fake-key"

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (
    BASE_DIR.parent / 'reversion_compare' / 'locale',
)

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # Speeding up the tests

SITE_ID = 1

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",

    "debug_toolbar",

    "reversion",
    "reversion_compare",
    "reversion_compare_tests",
]

ROOT_URLCONF = "reversion_compare_tests.urls"

STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR.parent / 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR.parent / 'media')

INTERNAL_IPS = [
    '127.0.0.1',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(Path(BASE_DIR.parent, "test_project_db.sqlite3")),
        # 'NAME': ":memory:",
        'OPTIONS': {
            # https://docs.djangoproject.com/en/2.2/ref/databases/#database-is-locked-errors
            'timeout': 20,
        }
    }
}

DEBUG = True

# add reversion models to django admin:
ADD_REVERSION_ADMIN = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d %(message)s',

        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django_tools': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'revision_compare': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'revision_compare_tests': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
