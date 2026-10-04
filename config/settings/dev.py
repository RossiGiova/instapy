"""Local development settings (default for manage.py)."""

from .base import *  # noqa: F401,F403
from .base import env_bool, env_list
import os

DEBUG = env_bool("DJANGO_DEBUG", True)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key-do-not-use-in-production")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
