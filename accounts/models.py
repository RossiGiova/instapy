from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q
from django.templatetags.static import static

from core.fields import NicknameField
from core.validators import validate_image_size

username_validator = RegexValidator(
    regex=r"^(?=.*[a-z_.])[a-z0-9._]+$",
    message="Usa solo lettere minuscole, numeri, punto e underscore (non solo numeri).",
)


class User(AbstractUser):
    """Custom user. `username` is the public nickname (always lowercase)."""

    class Gender(models.TextChoices):
        UNSPECIFIED = "N", "Non specificato"
        MALE = "M", "Maschio"
        FEMALE = "F", "Femmina"

    username = NicknameField(
        "nickname",
        max_length=20,
        unique=True,
        validators=[username_validator],
        error_messages={"unique": "Questo nickname è già in uso."},
    )
    email = models.EmailField(
        "indirizzo email",
        unique=True,
        error_messages={"unique": "Esiste già un account con questa email."},
    )
    birth_date = models.DateField("data di nascita", null=True, blank=True)
    bio = models.CharField("biografia", max_length=150, blank=True)
    gender = models.CharField("sesso", max_length=1, choices=Gender.choices, default=Gender.UNSPECIFIED)
    avatar = models.ImageField("foto profilo", upload_to="avatars/", blank=True, validators=[validate_image_size])
    verified = models.BooleanField("verificato", default=False)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ["id"]
        verbose_name = "utente"
        verbose_name_plural = "utenti"

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else static("img/default-avatar.png")

    @property
    def display_name(self):
        return self.get_full_name() or self.username


class Follow(models.Model):
    """`follower` follows `following`."""

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "follow"
        verbose_name_plural = "follow"
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow"),
            models.CheckConstraint(condition=~Q(follower=F("following")), name="no_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower} → {self.following}"
