"""Helpers shared by the test suites."""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from accounts.models import User
from posts.models import Post


def make_image(name="photo.jpg", color=(200, 30, 30)):
    buffer = io.BytesIO()
    Image.new("RGB", (40, 40), color).save(buffer, "JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


def make_user(username="mario", password="Sup3r-secret-pw", **extra):
    extra.setdefault("email", f"{username}@example.com")
    return User.objects.create_user(username=username, password=password, **extra)


def make_post(author, description="hello"):
    return Post.objects.create(author=author, image=make_image(), description=description)
