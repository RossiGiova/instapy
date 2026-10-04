from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_size(image):
    """Reject uploads bigger than settings.MAX_UPLOAD_SIZE."""
    if image.size > settings.MAX_UPLOAD_SIZE:
        limit_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        raise ValidationError(f"L'immagine è troppo grande (massimo {limit_mb} MB).")
