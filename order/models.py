import uuid

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Menunggu pembayaran"
        PROCESSING = "processing", "Diproses"
        SHIPPED = "shipped", "Dikirim / siap diambil"
        COMPLETED = "completed", "Selesai"
        CANCELLED = "cancelled", "Dibatalkan"

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Bayar saat diterima (COD)"
        DEMO = "demo", "Pembayaran simulasi"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Belum dibayar"
        PAID = "paid", "Sudah dibayar"
        REFUNDED = "refunded", "Dikembalikan (simulasi)"

    class DeliveryMethod(models.TextChoices):
        PICKUP = "pickup", "Ambil di kampus UI"
        COURIER = "courier", "Kirim dengan kurir"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkout_key = models.UUIDField(unique=True, editable=False)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    recipient_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(max_length=1000)
    destination = models.CharField(max_length=300, blank=True)
    destination_id = models.PositiveIntegerField(null=True, blank=True)
    delivery_method = models.CharField(max_length=10, choices=DeliveryMethod.choices)
    shipping_service = models.CharField(max_length=150)
    shipping_etd = models.CharField(max_length=100, blank=True)
    shipping_cost = models.PositiveBigIntegerField(default=0)
    subtotal = models.PositiveBigIntegerField()
    total = models.PositiveBigIntegerField()
    weight_grams = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(max_length=500, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["buyer", "status", "-created_at"])]
        constraints = [
            models.CheckConstraint(condition=Q(total=F("subtotal") + F("shipping_cost")), name="order_total_matches_components"),
        ]

    @property
    def number(self):
        return f"SB-{timezone.localtime(self.created_at):%y%m%d}-{self.id.hex[:8].upper()}"

    @property
    def can_cancel(self):
        return self.status in {self.Status.PENDING, self.Status.PROCESSING}

    def get_absolute_url(self):
        return reverse("order:detail", args=[self.id])

    def __str__(self):
        return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("product.Product", on_delete=models.SET_NULL, null=True, related_name="order_items")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sold_order_items")
    product_name = models.CharField(max_length=200)
    seller_name = models.CharField(max_length=150)
    thumbnail = models.URLField(max_length=500, blank=True)
    condition = models.CharField(max_length=30)
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ["pk"]
        constraints = [models.CheckConstraint(condition=Q(quantity__gte=1), name="order_item_quantity_gte_1")]

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class OrderEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=12, choices=Order.Status.choices)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
