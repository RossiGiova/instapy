from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "verified", "is_staff")
    list_filter = UserAdmin.list_filter + ("verified",)
    fieldsets = UserAdmin.fieldsets + (
        ("Profilo", {"fields": ("bio", "birth_date", "gender", "avatar", "verified")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profilo", {"fields": ("email", "birth_date", "gender")}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
