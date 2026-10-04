#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:  # python-dotenv is optional
        pass
    default_settings = "config.settings.test" if sys.argv[1:2] == ["test"] else "config.settings.dev"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and is your virtual "
            "environment activated? (pip install -r requirements.txt)"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
