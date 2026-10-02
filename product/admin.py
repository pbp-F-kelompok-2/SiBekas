"""Admin registrations for the product module."""

from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "condition")
    list_filter = ("category", "condition")
    search_fields = ("name",)
    inlines = [ProductImageInline]
