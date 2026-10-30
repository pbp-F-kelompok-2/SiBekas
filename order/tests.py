import json
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import signing
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from cart.models import Cart, CartItem
from cart.services import cart_summary
from product.models import Category, Product

from .models import Order
from .services import OrderError, change_status, checkout_token, create_order


@override_settings(ORDER_ENABLE_DEMO_PAYMENT=True)
class OrderFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.buyer = User.objects.create_user(username="buyer", email="buyer@ui.ac.id", password="TestPassword123!")
        cls.other = User.objects.create_user(username="other")
        cls.staff = User.objects.create_user(username="staff", is_staff=True)
        cls.category = Category.objects.create(name="Buku")
        cls.product = Product.objects.create(name="Buku PBP", category=cls.category, price=75000, stock=5, weight_grams=600, seller=cls.other)

    def setUp(self):
        self.client.force_login(self.buyer)
        self.cart = Cart.objects.create(user=self.buyer)
        self.item = self.cart.items.create(product=self.product, quantity=2)

    def payload(self, **changes):
        data = {
            "recipient_name": "Faris", "phone_number": "081234567890", "address": "Perpustakaan UI, Depok",
            "delivery_method": "pickup", "payment_method": "cod", "notes": "Titip di lobi",
            "checkout_token": checkout_token(self.buyer, cart_summary(self.buyer)), "shipping_quote": "",
        }
        return {**data, **changes}

    def make_order(self, **changes):
        return create_order(self.buyer, self.payload(**changes))

    def assert_stock(self, expected):
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, expected)

    def test_checkout_uses_database_totals_and_reserves_stock(self):
        data = self.payload(total=1, shipping_cost=1, price=1)
        response = self.client.post(reverse("order:checkout"), data)
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual((order.subtotal, order.shipping_cost, order.total), (150000, 0, 150000))
        self.assertEqual(order.weight_grams, 1200)
        self.assertEqual(order.status, "processing")
        self.assertEqual(order.items.get().quantity, 2)
        self.assertEqual(order.events.count(), 1)
        self.assertFalse(self.cart.items.exists())
        self.assert_stock(3)

    def test_repeated_checkout_returns_same_order(self):
        data = self.payload()
        self.client.post(reverse("order:checkout"), data)
        response = self.client.post(reverse("order:checkout"), data)
        self.assertEqual(Order.objects.count(), 1)
        self.assertRedirects(response, Order.objects.get().get_absolute_url())
        self.assert_stock(3)

    def test_stale_price_rejected_without_mutation(self):
        data = self.payload()
        Product.objects.filter(pk=self.product.pk).update(price=100000)
        response = self.client.post(reverse("order:checkout"), data)
        self.assertContains(response, "harga keranjang berubah")
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.cart.items.exists())
        self.assert_stock(5)

    def test_unavailable_stock_does_not_create_order(self):
        data = self.payload()
        Product.objects.filter(pk=self.product.pk).update(stock=1)
        response = self.client.post(reverse("order:checkout"), data)
        self.assertRedirects(response, reverse("cart:index"))
        self.assertFalse(Order.objects.exists())
        self.assert_stock(1)

    def test_missing_cart_product_blocks_checkout(self):
        self.cart.items.create(product=None, quantity=1)
        response = self.client.get(reverse("order:checkout"))
        self.assertRedirects(response, reverse("cart:index"))

    def test_cannot_buy_own_product(self):
        Product.objects.filter(pk=self.product.pk).update(seller=self.buyer)
        with self.assertRaises(OrderError):
            self.make_order()

    def test_snapshot_survives_product_edit_and_delete(self):
        order = self.make_order()
        self.product.name = "Buku Edisi Baru"
        self.product.price = 90000
        self.product.save()
        item = order.items.get()
        self.assertEqual(item.product_name, "Buku PBP")
        self.assertEqual(item.unit_price, 75000)

    def test_status_transitions_and_permissions(self):
        order = self.make_order(payment_method="demo")
        self.assertEqual(order.status, "pending")
        self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "pay"})
        order.refresh_from_db()
        self.assertEqual(order.status, "processing")
        self.assertEqual(order.payment_status, "paid")

        self.client.force_login(self.staff)
        self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "ship"})
        order.refresh_from_db()
        self.assertEqual(order.status, "shipped")

        self.client.force_login(self.buyer)
        self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "complete"})
        order.refresh_from_db()
        self.assertEqual(order.status, "completed")

    def test_cancellation_restores_stock(self):
        order = self.make_order()
        self.assert_stock(3)
        self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "cancel"})
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.assert_stock(5)

    def test_required_fields_and_phone_validation(self):
        for changes in ({"phone_number": "abc"}, {"address": " "}, {"recipient_name": ""}):
            with self.subTest(changes=changes):
                response = self.client.post(reverse("order:checkout"), self.payload(**changes))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
        self.assertFalse(Order.objects.exists())

    def test_transaction_rolls_back_if_stock_update_fails(self):
        with patch("order.services.Product.objects.filter") as mock_filter:
            mock_filter.return_value.update.return_value = 0
            with self.assertRaises(OrderError):
                self.make_order()
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.cart.items.exists())
        self.assert_stock(5)

    def test_history_filter_search_and_staff_management(self):
        order = self.make_order()
        self.assertContains(self.client.get(reverse("order:index"), {"status": "processing", "q": "PBP"}), order.number)
        self.assertNotContains(self.client.get(reverse("order:index"), {"status": "completed"}), order.number)
        self.client.force_login(self.staff)
        self.assertNotContains(self.client.get(reverse("order:index")), order.number)
        self.assertContains(self.client.get(reverse("order:index"), {"view": "manage"}), order.number)
        self.assertEqual(self.client.get(order.get_absolute_url()).status_code, 200)

    def test_order_total_database_constraint(self):
        order = self.make_order()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.filter(pk=order.pk).update(total=1)

    def test_endpoints_return_valid_json(self):
        dest_res = self.client.get(reverse("order:destinations"))
        self.assertEqual(dest_res.status_code, 200)
        quote_res = self.client.post(reverse("order:shipping_quotes"))
        self.assertEqual(quote_res.status_code, 200)

    def test_checkout_selected_items_only(self):
        second_product = Product.objects.create(
            name="Mouse PBP",
            category=self.category,
            price=100000,
            stock=4,
            weight_grams=200,
            seller=self.other,
        )
        second_item = self.cart.items.create(
            product=second_product,
            quantity=1,
        )
        selected_ids = [self.item.pk]
        summary = cart_summary(self.buyer, item_ids=selected_ids)
        token = checkout_token(self.buyer, summary, item_ids=selected_ids)
        response = self.client.post(
            reverse("order:checkout"),
            self.payload(checkout_token=token),
        )
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.get().product_name, "Buku PBP")
        self.assertFalse(self.cart.items.filter(pk=self.item.pk).exists())
        self.assertTrue(self.cart.items.filter(pk=second_item.pk).exists())
        self.assertEqual(order.subtotal, 150000)

    def test_courier_shipping_with_agenwebsite_quote(self):
        data = self.payload(
            delivery_method="courier",
            destination_postal_code="10110",
            address="Jl. Medan Merdeka Barat No. 1, Jakarta Pusat",
        )
        response = self.client.post(reverse("order:checkout"), data)
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(order.delivery_method, "courier")
        self.assertGreater(order.shipping_cost, 0)
        self.assertEqual(order.total, order.subtotal + order.shipping_cost)

    def test_two_person_checkout_seller_ship_and_buyer_complete(self):
        # 1. Product owned by self.other (seller) with stock=2
        Product.objects.filter(pk=self.product.pk).update(stock=2)
        # Buyer checks out 2 items (emptying remaining stock)
        data = self.payload()
        response = self.client.post(reverse("order:checkout"), data)
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(order.status, "processing")
        self.assert_stock(0)

        # 2. Check seller dashboard for seller (self.other)
        self.client.force_login(self.other)
        seller_dash = self.client.get(reverse("order:seller_dashboard"))
        self.assertEqual(seller_dash.status_code, 200)
        # Because stock is 0, it is no longer in active selling_products
        self.assertNotIn(self.product, seller_dash.context["selling_products"])
        # The order is in in_checkout_orders
        self.assertIn(order, seller_dash.context["in_checkout_orders"])

        # 3. Seller marks order as shipped / handed over
        self.client.post(
            reverse("order:update_status", args=[order.pk]),
            {"action": "ship", "tracking_number": "JNT-CAMPUS-999"},
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "shipped")
        self.assertEqual(order.tracking_number, "JNT-CAMPUS-999")

        # 4. Buyer completes the order (Selesaikan Barang)
        self.client.force_login(self.buyer)
        self.client.post(
            reverse("order:update_status", args=[order.pk]),
            {"action": "complete"},
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "completed")
        self.assertEqual(order.payment_status, "paid")

        # 5. Seller checks dashboard: order is now in completed_orders (history)
        self.client.force_login(self.other)
        seller_dash_after = self.client.get(reverse("order:seller_dashboard"))
        self.assertNotIn(order, seller_dash_after.context["in_checkout_orders"])
        self.assertIn(order, seller_dash_after.context["completed_orders"])
        self.assertGreater(seller_dash_after.context["total_revenue"], 0)
