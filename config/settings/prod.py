"""Production settings: everything sensitive comes from the environment."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import env_bool, env_list

DEBUG = env_bool("DJANGO_DEBUG", False)

try:
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
except KeyError as exc:
    raise ImproperlyConfigured("Set the DJANGO_SECRET_KEY environment variable.") from exc

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_CONTENT_TYPE_NOSNIFF = True
