from io import StringIO
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import OperationalError
from django.test import TestCase, override_settings
from django.urls import reverse

from cart.models import Cart
from cart.services import cart_summary
from order.models import Order
from order.services import OrderError, checkout_token, create_order
from product.models import Category, Product
from profiles.models import Favorite, Profile


@override_settings(ORDER_ENABLE_DEMO_PAYMENT=True)
class PurchaseIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.buyer = users.objects.create_user(username="integrated-buyer", email="integrated-buyer@ui.ac.id")
        cls.seller = users.objects.create_user(username="integrated-seller")
        cls.staff = users.objects.create_user(username="integrated-staff", is_staff=True)
        cls.category = Category.objects.create(name="Integration")
        cls.product = Product.objects.create(name="Buku Integrasi", price=75000, stock=4, seller=cls.seller, category=cls.category)
        cls.profile = Profile.objects.create(user=cls.buyer, full_name="Pembeli UI", phone_number="+62 812-3456-7890", address="Perpustakaan UI")

    def setUp(self):
        self.client.force_login(self.buyer)

    def payload(self, **changes):
        cart, _ = Cart.objects.get_or_create(user=self.buyer)
        cart.items.get_or_create(product=self.product, defaults={"quantity": 2})
        return {
            "recipient_name": "Pembeli UI", "phone_number": "+62 812-3456-7890", "address": "Perpustakaan UI",
            "delivery_method": "pickup", "payment_method": "cod",
            "checkout_token": checkout_token(self.buyer, cart_summary(self.buyer)), **changes,
        }

    def test_purchase_from_cart_through_public_review_and_profile(self):
        self.client.post(reverse("cart:add_item"), {"product_id": self.product.pk, "quantity": 2})
        checkout = self.client.get(reverse("order:checkout"))
        self.assertEqual(checkout.context["form"].initial["phone_number"], self.profile.phone_number)
        token = checkout.context["form"].initial["checkout_token"]
        response = self.client.post(reverse("order:checkout"), self.payload(checkout_token=token))
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual((order.phone_number, order.total), ("+6281234567890", 150000))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
        self.assertContains(self.client.get(reverse("order:index")), order.number)
        self.client.force_login(self.staff)
        self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "ship"})
        self.client.force_login(self.buyer)
        self.client.post(reverse("order:update_status", args=[order.pk]), {"action": "complete"})
        order.refresh_from_db()
        self.assertEqual((order.status, order.payment_status), ("completed", "paid"))
        self.client.post(reverse("review:create", args=[self.product.pk]), {"rating": 5, "comment": "Barang sesuai deskripsi integrasi."})
        profile = self.client.get(reverse("profile:index"))
        self.assertEqual((profile.context["total_orders"], profile.context["total_reviews"]), (1, 1))
        self.client.logout()
        detail = self.client.get(self.product.get_absolute_url())
        self.assertContains(detail, "Barang sesuai deskripsi integrasi.")
        self.assertEqual(detail.context["average_rating"], 5)

    def test_order_history_prevents_account_deletion_without_losing_session(self):
        order = create_order(self.buyer, self.payload())
        response = self.client.post(reverse("profile:delete_account"), follow=True)
        self.assertContains(response, "memiliki riwayat pesanan")
        self.assertTrue(get_user_model().objects.filter(pk=self.buyer.pk).exists())
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.buyer.pk)

    def test_account_without_orders_can_still_be_deleted(self):
        response = self.client.post(reverse("profile:delete_account"))
        self.assertRedirects(response, reverse("product:index"))
        self.assertFalse(get_user_model().objects.filter(pk=self.buyer.pk).exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_invalid_profile_edit_preserves_input_and_errors(self):
        response = self.client.post(reverse("profile:edit"), {
            "full_name": "Pembeli Baru", "faculty": "Fasilkom", "student_id": "invalid",
            "phone_number": "081234567890", "address": "UI", "bio": "Catatan pengguna",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("student_id", response.context["form"].errors)
        self.assertContains(response, "Catatan pengguna")
        # Modal harus terbuka. Cek kelas `is-open` pada elemen overlay tanpa bergantung pada urutan/daftar kelas Tailwind.
        self.assertRegex(
            response.content.decode(),
            r'class="[^"]*\bedit-profile-overlay\b[^"]*\bis-open\b[^"]*"',
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, "Pembeli UI")

    def test_product_without_category_can_be_saved_on_migrated_database(self):
        response = self.client.post(reverse("product:create"), {
            "name": "Barang tanpa kategori", "description": "Barang mahasiswa", "price": 50000,
            "stock": 1, "condition": "good", "weight_grams": 500,
        })
        self.assertRedirects(response, reverse("profile:index"))
        self.assertIsNone(Product.objects.get(name="Barang tanpa kategori").category_id)

    def test_catalog_pagination_preserves_all_selected_filters(self):
        for index in range(13):
            Product.objects.create(name=f"Buku {index}", price=1000, stock=1, seller=self.buyer, category=self.category)
        params = {"q": "Buku", "category": self.category.slug, "mine": "1", "condition": "good", "min_price": "100", "max_price": "2000", "sort": "cheap"}
        response = self.client.get(reverse("product:index"), params)
        prefix = response.context["page_url_prefix"]
        for key, value in params.items():
            self.assertIn(f"{key}={value}", prefix)
        self.assertContains(response, "&amp;page=2")

    def test_favorite_button_uses_current_user(self):
        Favorite.objects.create(user=self.seller, product=self.product)
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, "Tambah ke favorit")
        self.assertNotContains(response, "Hapus dari favorit")
        Favorite.objects.create(user=self.buyer, product=self.product)
        self.assertContains(self.client.get(self.product.get_absolute_url()), "Hapus dari favorit")

    def test_service_rejects_invalid_delivery_and_phone_without_mutation(self):
        for changes in [{"delivery_method": "invalid"}, {"phone_number": "bad"}]:
            with self.subTest(changes=changes), self.assertRaises(OrderError):
                create_order(self.buyer, self.payload(**changes))
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)
        self.assertTrue(self.buyer.cart.items.exists())


class DeploymentReadinessTests(TestCase):
    @patch("product.management.commands.seed_products.urlopen")
    def test_initial_seed_preserves_existing_stock_and_product_edits(self, urlopen):
        category = Category.objects.create(name="Buku")
        existing = Product.objects.create(name="Nama diubah penjual", price=1500, stock=2, category=category, dummyjson_id=1)
        rows = [{"id": number, "title": f"Initial {number}", "description": "Seed", "price": 1,
                 "stock": 99, "brand": "", "thumbnail": "https://example.com/photo.jpg", "images": [], "category": "books"}
                for number in range(1, 51)]
        urlopen.return_value.__enter__.return_value.read.return_value = json.dumps({"products": rows})
        with override_settings(SEED_INITIAL_PRODUCTS=True):
            call_command("bootstrap_catalog", stdout=StringIO())
            call_command("bootstrap_catalog", stdout=StringIO())
        existing.refresh_from_db()
        self.assertEqual((existing.name, existing.price, existing.stock), ("Nama diubah penjual", 1500, 2))
        self.assertEqual(Product.objects.count(), 50)
        self.assertEqual(urlopen.call_count, 1)

    @override_settings(SEED_INITIAL_PRODUCTS=False)
    @patch("product.management.commands.seed_products.urlopen")
    def test_release_does_not_seed_without_explicit_configuration(self, urlopen):
        call_command("bootstrap_catalog", stdout=StringIO())
        urlopen.assert_not_called()
        self.assertFalse(Product.objects.exists())

    def test_strict_readiness_rejects_missing_catalog_staff(self):
        with self.assertRaises(CommandError):
            call_command("check_order_readiness", strict=True, stdout=StringIO())

    @patch("sibekas.views.connection.cursor", side_effect=OperationalError("private database error"))
    def test_health_failure_returns_503_without_database_details(self, cursor):
        response = self.client.get(reverse("health-check"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable", "database": "unavailable"})
