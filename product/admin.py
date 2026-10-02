"""Admin registrations for the product module."""

from django.contrib import admin

from .models import Category, Product, ProductImage, ProductLike


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "condition",
        "is_active",
        "source",
        "created_at",
    )
    list_filter = ("is_active", "condition", "source", "category")
    search_fields = ("name", "brand", "description")
    list_select_related = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("source", "external_id", "created_at", "updated_at")
    inlines = [ProductImageInline]

@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "created_at")
    search_fields = ("product__name", "user__username")
    list_select_related = ("product", "user")