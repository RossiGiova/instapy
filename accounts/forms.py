from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.forms import BootstrapFormMixin

from .models import User


def _validate_birth_date(value):
    if value and value >= date.today():
        raise forms.ValidationError("La data di nascita deve essere nel passato.")
    return value


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    birth_date = forms.DateField(
        label="Data di nascita",
        widget=forms.DateInput(attrs={"type": "date"}),
        validators=[_validate_birth_date],
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birth_date", "username", "gender")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Esiste già un account con questa email.")
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Nicknames are case-insensitive: they are always stored in lowercase."""

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "bio", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "avatar": forms.FileInput(attrs={"accept": "image/png,image/jpeg"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Esiste già un account con questa email.")
        return email


class AccountDeleteForm(BootstrapFormMixin, forms.Form):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("Password errata.")
        return password
