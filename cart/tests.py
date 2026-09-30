from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Cart, CartItem


User = get_user_model()


class CartModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rheza",
            password="testpass123",
        )

        self.cart = Cart.objects.create(
            user=self.user,
        )

    def test_user_has_one_cart(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Cart.objects.create(
                    user=self.user,
                )

    def test_cart_item_can_be_created(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product_reference="product-001",
            quantity=1,
        )

        self.assertEqual(
            item.cart,
            self.cart,
        )

        self.assertEqual(
            item.quantity,
            1,
        )

    def test_same_product_cannot_be_duplicated_in_cart(self):
        CartItem.objects.create(
            cart=self.cart,
            product_reference="product-001",
            quantity=1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CartItem.objects.create(
                    cart=self.cart,
                    product_reference="product-001",
                    quantity=1,
                )

    def test_quantity_cannot_be_zero(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CartItem.objects.create(
                    cart=self.cart,
                    product_reference="product-002",
                    quantity=0,
                )


class CartViewTests(TestCase):
    def test_cart_page_is_accessible(self):
        response = self.client.get(
            reverse("cart:index")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "cart/index.html",
        )

    def test_cart_page_contains_available_items(self):
        response = self.client.get(
            reverse("cart:index")
        )

        self.assertContains(
            response,
            "Barang tersedia",
        )

        self.assertContains(
            response,
            "Buku Dasar-Dasar Pemrograman Python",
        )

    def test_cart_page_contains_unavailable_section(self):
        response = self.client.get(
            reverse("cart:index")
        )

        self.assertContains(
            response,
            "Tidak tersedia",
        )

        self.assertContains(
            response,
            "Barang sudah terjual",
        )

    def test_cart_page_contains_summary(self):
        response = self.client.get(
            reverse("cart:index")
        )

        self.assertContains(
            response,
            "Ringkasan Belanja",
        )

        self.assertContains(
            response,
            "Lanjut ke Checkout",
        )

    def test_add_item_requires_post(self):
        response = self.client.get(
            reverse("cart:add_item")
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_update_item_requires_post(self):
        response = self.client.get(
            reverse(
                "cart:update_item",
                args=[1],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_remove_item_requires_post(self):
        response = self.client.get(
            reverse(
                "cart:remove_item",
                args=[1],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_post_cart_actions_redirect_to_cart(self):
        add_response = self.client.post(
            reverse("cart:add_item")
        )

        update_response = self.client.post(
            reverse(
                "cart:update_item",
                args=[1],
            )
        )

        remove_response = self.client.post(
            reverse(
                "cart:remove_item",
                args=[1],
            )
        )

        expected_url = reverse(
            "cart:index"
        )

        self.assertRedirects(
            add_response,
            expected_url,
        )

        self.assertRedirects(
            update_response,
            expected_url,
        )

        self.assertRedirects(
            remove_response,
            expected_url,
        )