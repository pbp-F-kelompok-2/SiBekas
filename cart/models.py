"""Cart models are developed in the cart feature branch."""

from django.conf import settings
from django.db import models
from django.db.models import Q
from product.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.product} "
            f"x {self.quantity}"
        )

    @property
    def line_total(self):
        if not self.product:
            return 0

        return self.product.price * self.quantity

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "product",
                ],
                name="unique_product_per_cart",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name="cart_item_quantity_gte_1",
            ),
        ]