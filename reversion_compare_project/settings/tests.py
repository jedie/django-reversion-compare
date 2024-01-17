# flake8: noqa: E405
"""
    Settings used to run tests
"""
from reversion_compare_project.settings.prod import *  # noqa


ALLOWED_HOSTS = ['testserver']


# _____________________________________________________________________________
# Manage Django Project

INSTALLED_APPS.append('manage_django_project')

# _____________________________________________________________________________


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'No individual secret for tests ;)'

DEBUG = True

# Speedup tests by change the Password hasher:
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

# _____________________________________________________________________________

# All tests should use django-override-storage!
# Set root to not existing path, so that wrong tests will fail:
STATIC_ROOT = '/not/exists/static/'
MEDIA_ROOT = '/not/exists/media/'
