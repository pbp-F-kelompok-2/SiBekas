import json
import uuid
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.core import signing
from django.db import IntegrityError, transaction
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from cart.models import Cart, CartItem
from cart.services import cart_summary
from product.models import Category, Product

from .models import Order
from .services import OrderError, change_status, checkout_token, create_order
from .shipping import ShippingError, calculate_quotes, search_destinations, validate_quote


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
        Product.objects.filter(pk=self.product.pk).update(name="Nama baru", price=1)
        self.product.delete()
        item = order.items.get()
        self.assertEqual(item.product_name, "Buku PBP")
        self.assertEqual(item.line_total, 150000)
        self.assertIsNone(item.product_id)
        self.assertContains(self.client.get(order.get_absolute_url()), "Buku PBP")

    def test_cancel_restores_stock_only_once(self):
        order = self.make_order()
        change_status(order.pk, self.buyer, "cancel")
        self.assert_stock(5)
        with self.assertRaises(OrderError):
            change_status(order.pk, self.buyer, "cancel")
        self.assert_stock(5)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.assertEqual(order.events.count(), 2)

    def test_full_cod_lifecycle_and_review_eligibility(self):
        order = self.make_order()
        self.assertEqual(self.client.get(reverse("review:create", args=[self.product.pk])).status_code, 404)
        change_status(order.pk, self.staff, "ship")
        change_status(order.pk, self.buyer, "complete")
        order.refresh_from_db()
        self.assertEqual((order.status, order.payment_status), ("completed", "paid"))
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(order.completed_at)
        self.assertEqual(self.client.get(reverse("review:create", args=[self.product.pk])).status_code, 200)
        review_response = self.client.post(reverse("review:create", args=[self.product.pk]), {"rating": 5, "comment": "Sesuai deskripsi."})
        self.assertRedirects(review_response, reverse("review:index"))
        self.assertTrue(self.buyer.reviews.filter(product=self.product).exists())
        with self.assertRaises(OrderError):
            change_status(order.pk, self.buyer, "cancel")
        self.assert_stock(3)

    def test_demo_payment_and_refund(self):
        order = self.make_order(payment_method="demo")
        self.assertEqual(order.status, "pending")
        change_status(order.pk, self.buyer, "pay")
        with self.assertRaises(OrderError):
            change_status(order.pk, self.buyer, "pay")
        change_status(order.pk, self.buyer, "cancel")
        order.refresh_from_db()
        self.assertEqual(order.payment_status, "refunded")
        self.assert_stock(5)

    def test_demo_can_be_disabled(self):
        with override_settings(ORDER_ENABLE_DEMO_PAYMENT=False):
            response = self.client.post(reverse("order:checkout"), self.payload(payment_method="demo"))
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Order.objects.exists())

    def test_buyers_cannot_ship_or_skip_statuses(self):
        order = self.make_order()
        for action in ("ship", "complete", "pay", "invalid"):
            with self.subTest(action=action), self.assertRaises(OrderError):
                change_status(order.pk, self.buyer, action)
        self.assertEqual(order.events.count(), 1)

    def test_cannot_cancel_after_dispatch(self):
        order = self.make_order()
        change_status(order.pk, self.staff, "ship")
        with self.assertRaises(OrderError):
            change_status(order.pk, self.buyer, "cancel")
        self.assert_stock(3)

    def test_other_user_cannot_access_or_update_order(self):
        order = self.make_order()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(order.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "cancel"}).status_code, 404)
        self.assertNotContains(self.client.get(reverse("order:index")), order.number)
        with self.assertRaises(OrderError):
            change_status(order.pk, self.other, "cancel")

    def test_status_endpoint_requires_post_and_csrf(self):
        order = self.make_order()
        url = reverse("order:update_status", args=[order.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.buyer)
        self.assertEqual(csrf_client.post(url, {"action": "cancel"}).status_code, 403)

    def test_guest_is_redirected_to_login(self):
        self.client.logout()
        for route in ("order:index", "order:checkout"):
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("profile:login"), response.url)

    def test_login_preserves_safe_checkout_destination(self):
        self.client.logout()
        for next_url, expected in [("/orders/checkout/", "/orders/checkout/"), ("https://evil.example/", reverse("profile:index"))]:
            with self.subTest(next_url=next_url):
                response = self.client.post(reverse("profile:login"), {"email": "buyer@ui.ac.id", "password": "TestPassword123!", "next": next_url})
                self.assertRedirects(response, expected)
                self.client.logout()

    def test_forged_or_other_user_token_rejected(self):
        foreign = checkout_token(self.other, cart_summary(self.buyer))
        for token in ("forged", foreign):
            with self.subTest(token=token[:10]):
                response = self.client.post(reverse("order:checkout"), self.payload(checkout_token=token))
                self.assertContains(response, "Sesi checkout kedaluwarsa")
        self.assertFalse(Order.objects.exists())

    def test_expired_checkout_token_rejected(self):
        with patch("django.core.signing.time.time", return_value=1):
            data = self.payload()
        response = self.client.post(reverse("order:checkout"), data)
        self.assertContains(response, "Sesi checkout kedaluwarsa")
        self.assertFalse(Order.objects.exists())

    def test_required_fields_and_phone_validation(self):
        for changes in ({"phone_number": "abc"}, {"address": " "}, {"recipient_name": ""}):
            with self.subTest(changes=changes):
                response = self.client.post(reverse("order:checkout"), self.payload(**changes))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
        self.assertFalse(Order.objects.exists())

    def shipping_token(self, **changes):
        summary = cart_summary(self.buyer)
        quote = {"cost": 18000, "service": "JNE · REG", "etd": "1-2 day", "destination": "BEJI, DEPOK", "destination_id": 123, "user": self.buyer.pk, "fingerprint": summary["fingerprint"], "weight": summary["weight_grams"]}
        return signing.dumps({**quote, **changes}, salt="order.shipping")

    def test_courier_checkout_uses_signed_quote_and_requires_tracking(self):
        response = self.client.post(reverse("order:checkout"), self.payload(delivery_method="courier", payment_method="demo", shipping_quote=self.shipping_token(), shipping_cost=1))
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual((order.shipping_cost, order.total, order.destination_id), (18000, 168000, 123))
        change_status(order.pk, self.buyer, "pay")
        with self.assertRaises(OrderError):
            change_status(order.pk, self.staff, "ship")
        change_status(order.pk, self.staff, "ship", tracking_number="JNE12345")
        order.refresh_from_db()
        self.assertEqual(order.tracking_number, "JNE12345")

    def test_forged_expired_or_foreign_shipping_quote_rejected(self):
        with patch("django.core.signing.time.time", return_value=1):
            expired = self.shipping_token()
        for token in ("forged", expired, self.shipping_token(user=self.other.pk), self.shipping_token(fingerprint="changed")):
            response = self.client.post(reverse("order:checkout"), self.payload(delivery_method="courier", payment_method="demo", shipping_quote=token))
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Order.objects.exists())
        self.assert_stock(5)

    def test_courier_requires_quote_and_disallows_unsupported_cod(self):
        response = self.client.post(reverse("order:checkout"), self.payload(delivery_method="courier"))
        self.assertIn("shipping_quote", response.context["form"].errors)
        self.assertIn("payment_method", response.context["form"].errors)
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

    @patch("order.views.search_destinations", return_value=[{"label": "BEJI", "token": "signed"}])
    def test_destination_endpoint(self, mock_search):
        url = reverse("order:destinations")
        self.assertEqual(self.client.get(url, {"q": "ab"}).status_code, 400)
        response = self.client.get(url, {"q": "Beji"})
        self.assertEqual(response.json()["destinations"][0]["label"], "BEJI")
        mock_search.assert_called_once_with("Beji", self.buyer.pk)

    @override_settings(RAJAONGKIR_API_KEY="", RAJAONGKIR_ORIGIN_ID="")
    def test_missing_shipping_credentials_returns_friendly_error(self):
        response = self.client.get(reverse("order:destinations"), {"q": "Beji"})
        self.assertEqual(response.status_code, 503)
        self.assertIn("belum tersedia", response.json()["error"])


@override_settings(RAJAONGKIR_API_KEY="test-key", RAJAONGKIR_ORIGIN_ID="100", RAJAONGKIR_COURIERS="jne:jnt")
class RajaOngkirTests(SimpleTestCase):
    def response(self, data):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"meta": {"code": 200}, "data": data}).encode()
        return response

    @patch("order.shipping.urlopen")
    def test_search_uses_official_endpoint_and_keeps_key_on_server(self, urlopen):
        urlopen.return_value = self.response([{"id": 123, "label": "BEJI, DEPOK"}])
        result = search_destinations("Beji Depok", 7)
        request = urlopen.call_args.args[0]
        self.assertIn("destination/domestic-destination?search=Beji+Depok", request.full_url)
        self.assertEqual(request.get_header("Key"), "test-key")
        self.assertNotIn("test-key", json.dumps(result))
        self.assertEqual(signing.loads(result[0]["token"], salt="order.destination")["id"], 123)

    @patch("order.shipping.urlopen")
    def test_cost_uses_weight_and_signed_destination(self, urlopen):
        urlopen.return_value = self.response([{"name": "JNE", "code": "jne", "service": "REG", "cost": 18000, "etd": "1-2 day"}])
        destination = signing.dumps({"id": 123, "label": "BEJI", "user": 7}, salt="order.destination")
        summary = {"weight_grams": 1200, "fingerprint": "cart-version"}
        quotes = calculate_quotes(destination, summary, 7)
        request = urlopen.call_args.args[0]
        self.assertTrue(request.full_url.endswith("calculate/domestic-cost"))
        self.assertIn(b"weight=1200", request.data)
        self.assertIn(b"origin=100", request.data)
        self.assertIn(b"destination=123", request.data)
        self.assertEqual(validate_quote(quotes[0]["token"], summary, 7)["cost"], 18000)

    @patch("order.shipping.urlopen", side_effect=URLError("unavailable"))
    def test_api_network_failure_is_handled(self, urlopen):
        with self.assertRaises(ShippingError):
            search_destinations("Beji", 7)

    @patch("order.shipping.urlopen")
    def test_malformed_api_response_is_handled(self, urlopen):
        urlopen.return_value = self.response([{"invalid": "data"}])
        with self.assertRaises(ShippingError):
            search_destinations("Beji", 7)
