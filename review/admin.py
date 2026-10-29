"""Admin registrations for the review module."""

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at", "edited")
    list_filter = ("rating", "edited", "created_at")
    search_fields = ("user__username", "product__name", "comment")
