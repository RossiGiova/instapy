from django import forms
from django.db import models


class LowercaseCharField(forms.CharField):
    """Form field that lowercases input *before* validators run."""

    def to_python(self, value):
        value = super().to_python(value)
        return value.lower() if value else value


class NicknameField(models.CharField):
    """CharField whose form field is case-insensitive (stored in lowercase)."""

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", LowercaseCharField)
        return super().formfield(**kwargs)
