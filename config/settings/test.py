"""Used automatically by `python manage.py test`: fast password hashing."""

from .dev import *  # noqa: F401,F403

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
