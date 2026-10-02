"""Product models are developed in the product feature branch."""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, Exists, OuterRef, Q
from django.urls import reverse

class Category(models.Model):
    name = models.CharField("nama", max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField("deskripsi", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "kategori"
        verbose_name_plural = "kategori"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = build_unique_slug(Category, self.name, self.pk, max_length=120)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('product:index')}?category={self.slug}"


CONDITION_BADGES = {
    "new": ("accent", "sparkles"),
    "like_new": ("success", "circle-check"),
    "good": ("neutral", "thumbs-up"),
    "fair": ("warning", "circle-alert"),
}

class ProductQuerySet(models.QuerySet):
    def with_like_info(self, user):
        queryset = self.annotate(like_count=Count("likes", distinct=True))
        if user is not None and user.is_authenticated:
            liked = ProductLike.objects.filter(product=OuterRef("pk"), user=user)
            return queryset.annotate(is_liked=Exists(liked))
        return queryset.annotate(is_liked=models.Value(False, output_field=models.BooleanField()))

class Product(models.Model):
    class Condition(models.TextChoices):
        NEW = "new", "Baru"
        LIKE_NEW = "like_new", "Seperti Baru"
        GOOD = "good", "Kondisi Baik"
        FAIR = "fair", "Layak Pakai"

    class Source(models.TextChoices):
        MANUAL = "manual", "Listing pengguna"
        DUMMYJSON = "dummyjson", "Seed DummyJSON"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="penjual",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        help_text="Kosong untuk data awal hasil seed.",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="kategori",
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField("nama", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField("deskripsi")
    price = models.PositiveIntegerField(
        "harga (Rp)",
        validators=[MinValueValidator(1)],
    )
    stock = models.PositiveIntegerField("stok", default=1)
    condition = models.CharField(
        "kondisi",
        max_length=20,
        choices=Condition.choices,
        default=Condition.GOOD,
    )
    brand = models.CharField("merek", max_length=100, blank=True)
    weight_grams = models.PositiveIntegerField(
        "berat (gram)",
        default=500,
        validators=[MinValueValidator(1)],
        help_text="Dipakai untuk perhitungan ongkir (RajaOngkir).",
    )
    thumbnail_url = models.URLField("URL thumbnail", max_length=500, blank=True)
    is_active = models.BooleanField(
        "dipublikasikan",
        default=True,
        help_text="Nonaktifkan untuk menyembunyikan listing dari katalog.",
    )
    source = models.CharField(
        "sumber data",
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
    )
    external_id = models.PositiveIntegerField(
        "ID eksternal",
        null=True,
        blank=True,
        help_text="ID produk pada sumber eksternal (mis. DummyJSON).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()
    
    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "produk"
        verbose_name_plural = "produk"
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=Q(external_id__isnull=False),
                name="unique_product_external_id_per_source",
            ),
            models.CheckConstraint(
                condition=Q(price__gte=1),
                name="product_price_gte_1",
            ),
        ]
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = build_unique_slug(Product, self.name, self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product:detail", kwargs={"slug": self.slug})

    @property
    def is_available(self):
        return self.is_active and self.stock > 0

    @property
    def price_display(self):
        return f"Rp {self.price:,}".replace(",", ".")

    @property
    def condition_badge(self):
        variant, icon = CONDITION_BADGES.get(self.condition, ("neutral", "tag"))
        return {"variant": variant, "icon": icon, "label": self.get_condition_display()}

    @property
    def seller_name(self):
        return self.seller.username if self.seller else "SiBekas"

    @property
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
    alt_text = models.CharField("teks alternatif", max_length=200, blank=True)
    position = models.PositiveSmallIntegerField("urutan", default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "gambar produk"
        verbose_name_plural = "gambar produk"

    def __str__(self):
        return f"Gambar {self.position} - {self.product.name}"

class ProductLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_likes",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "like produk"
        verbose_name_plural = "like produk"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_like_per_user_product",
            ),
        ]

    def __str__(self):
        return f"{self.user} menyukai {self.product}"