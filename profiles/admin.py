"""Admin registrations for the profile module."""

from django.contrib import admin
from .models import Profile, Favorite


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "student_id", "faculty", "phone_number")
    search_fields = ("user__username", "user__email", "full_name", "student_id")
    list_filter = ("faculty",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
    list_filter = ("created_at",)
