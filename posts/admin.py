from django.contrib import admin

from .models import Comment, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "description", "created_at")
    list_filter = ("created_at",)
    search_fields = ("author__username", "description")
    raw_id_fields = ("author",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "text", "created_at")
    search_fields = ("author__username", "text")
    raw_id_fields = ("author", "post")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    raw_id_fields = ("user", "post")
