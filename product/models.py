"""Product models are developed in the product feature branch."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def build_unique_slug(model, text):
    base_slug = slugify(text) or "produk"
    slug = base_slug
    counter = 2
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = build_unique_slug(Category, self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    CONDITION_CHOICES = [
        ("new", "Baru"),
        ("like_new", "Seperti Baru"),
        ("good", "Baik"),
        ("fair", "Layak Pakai")
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="kategori",
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=1)
    condition = models.CharField(
        "kondisi",
        max_length=20,
        choices=CONDITION_CHOICES,
        default="good",
    )
    brand = models.CharField("merek", max_length=100, blank=True)
    weight_grams = models.PositiveIntegerField(
        "berat (gram)",
        default=500,
        help_text="Dipakai untuk perhitungan ongkir (RajaOngkir).",
    )

    thumbnail = models.URLField(max_length=500, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dummyjson_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "produk"
        verbose_name_plural = "produk"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = build_unique_slug(Product, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product:detail", args=[self.slug])

    def price_display(self):
        return f"Rp {self.price:,}".replace(",", ".")

    def is_sold_out(self):
        return self.stock == 0

    def seller_name(self):
        return self.seller.username if self.seller else "SiBekas"


    def main_image_url(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        first_image = self.images.first()
        return first_image.image_url if first_image else ""


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image_url = models.URLField("URL gambar", max_length=500)


    def __str__(self):
        return f"Gambar {self.product.name} - {self.product.name}"
