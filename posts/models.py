from django.conf import settings
from django.db import models
from django.db.models import Count, Exists, OuterRef, Prefetch, Value

from core.validators import validate_image_size


class PostQuerySet(models.QuerySet):
    def with_stats(self, user=None):
        """Annotate each post with `like_count`, `comment_count` and `liked_by_me`.

        Everything is computed in the database, so listing N posts costs a
        constant number of queries instead of N+1. The ordering is explicit
        because annotating with aggregates drops the model's default one.
        """
        qs = self.select_related("author").order_by("-created_at", "-id").annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )
        if user is not None and user.is_authenticated:
            qs = qs.annotate(
                liked_by_me=Exists(Like.objects.filter(post=OuterRef("pk"), user=user))
            )
        else:
            qs = qs.annotate(liked_by_me=Value(False, output_field=models.BooleanField()))
        return qs

    def prefetch_comments(self):
        return self.prefetch_related(
            Prefetch("comments", queryset=Comment.objects.select_related("author"))
        )


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField("foto", upload_to="posts/%Y/%m/", validators=[validate_image_size])
    description = models.CharField("descrizione", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "post"
        verbose_name_plural = "post"

    def __str__(self):
        return f"#{self.pk} di {self.author}: {self.description[:30]}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "like"
        verbose_name_plural = "like"
        constraints = [models.UniqueConstraint(fields=["user", "post"], name="unique_like")]

    def __str__(self):
        return f"{self.user} ♥ post #{self.post_id}"


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField("commento", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "commento"
        verbose_name_plural = "commenti"

    def __str__(self):
        return f"{self.author} su post #{self.post_id}: {self.text[:30]}"
