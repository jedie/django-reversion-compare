import os
import tempfile
from pathlib import Path

print("Use settings:", __file__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(BASE_DIR, "templates")],
        "OPTIONS": {
            "loaders": [
                (
                    "django_tools.template.loader.DebugCacheLoader",
                    (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader"
                    ),
                )
            ],
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "django.template.context_processors.static",
            ],
        },
    }
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "reversion.middleware.RevisionMiddleware",
)

LANGUAGE_CODE = "en"
LANGUAGES = (("en", "de"),)
SECRET_KEY = "unittests-fake-key"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # Speeding up the tests

SITE_ID = 1

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "reversion",
    "reversion_compare",
    "reversion_compare_tests",
]

ROOT_URLCONF = "reversion_compare_tests.urls"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# The temp path used for e.g.: models.FilePathField()
try:
    UNITTEST_TEMP_PATH = os.environ["UNITTEST_TEMP_PATH"]
except KeyError:
    UNITTEST_TEMP_PATH = tempfile.mkdtemp(prefix="reversion_compare_unittest_")
    print(f"Use temp dir: {UNITTEST_TEMP_PATH!r}")
    os.environ["UNITTEST_TEMP_PATH"] = UNITTEST_TEMP_PATH

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
