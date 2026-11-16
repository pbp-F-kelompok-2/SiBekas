"""Exercise mobile contracts against the same ORM and permissions as the web."""
import uuid

from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from cart.models import Cart, CartItem
from order.models import Order, OrderItem
from product.models import Category, Product
from profiles.models import Favorite, Profile
from review.models import Review


class MobileAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user("mobile_buyer", password="test-mobile-password")
        cls.seller = User.objects.create_user("mobile_seller", password="test-mobile-password")
        cls.other = User.objects.create_user("mobile_other", password="test-mobile-password")
        cls.category = Category.objects.create(name="Buku")
        cls.product = Product.objects.create(name="Buku Kalkulus", description="Buku kuliah layak pakai",
            price=45000, stock=2, seller=cls.seller, category=cls.category)
        cls.cart = Cart.objects.create(user=cls.buyer)
        cls.item = CartItem.objects.create(cart=cls.cart, product=cls.product, quantity=2)
        CartItem.objects.create(cart=Cart.objects.create(user=cls.other), product=cls.product)
        cls.profile = Profile.objects.create(user=cls.buyer, full_name="Mahasiswa UI", faculty="Fasilkom",
            student_id="2500000000", phone_number="081234567890", address="Depok")
        Favorite.objects.create(user=cls.buyer, product=cls.product)
        cls.order = Order.objects.create(checkout_key=uuid.uuid4(), buyer=cls.buyer,
            recipient_name="Mahasiswa", phone_number="081234567890", address="Kantin UI",
            delivery_method="pickup", shipping_service="Ambil kampus", subtotal=45000,
            total=45000, weight_grams=500, payment_method="cod")
        OrderItem.objects.create(order=cls.order, product=cls.product, seller=cls.seller,
            product_name=cls.product.name, seller_name=cls.seller.username,
            condition="Baik", unit_price=45000, quantity=1)
        cls.review = Review.objects.create(user=cls.buyer, product=cls.product, rating=5, comment="Buku terawat.")
        Review.objects.create(user=cls.other, product=cls.product, rating=4, comment="Sesuai deskripsi.")

    def setUp(self):
        cache.clear()

    def test_public_module_endpoints_and_pagination(self):
        self.assertEqual(self.client.get(reverse("api:root")).data["checkpoint"], 1)
        for route in ["product-list", "category-list", "review-list"]:
            response = self.client.get(reverse(f"api:{route}"))
            self.assertEqual(response.status_code, 200)
            self.assertIn("results", response.data)
            self.assertIn("next", response.data)
        response = self.client.get(reverse("api:product-list"))
        self.assertEqual(response.data["results"][0]["id"], self.product.pk)
        self.assertNotIn("email", response.data["results"][0])

    def test_search_filters_and_bad_queries(self):
        url = reverse("api:product-list")
        self.assertEqual(self.client.get(url, {"q": "KALKULUS"}).data["count"], 1)
        self.assertEqual(self.client.get(url, {"q": "tidak ada"}).data["count"], 0)
        self.assertEqual(self.client.get(url, {"category": self.category.slug}).data["count"], 1)
        for query in [{"min_price": "bad"}, {"min_price": -1}, {"condition": "invalid"},
                      {"min_price": 50000, "max_price": 1}]:
            self.assertEqual(self.client.get(url, query).status_code, 400)

    def test_product_detail_and_not_found(self):
        self.assertEqual(self.client.get(reverse("api:product-detail", args=[self.product.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("api:product-detail", args=[999999])).status_code, 404)

    def test_private_modules_require_login(self):
        for route in ["profile", "favorites", "cart", "order-list"]:
            self.assertEqual(self.client.get(reverse(f"api:{route}")).status_code, 401)

    def test_real_login_and_token_revocation(self):
        response = self.client.post(reverse("api:login"), {
            "username": self.buyer.username, "password": "test-mobile-password"}, format="json")
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]
        self.assertNotIn("password", response.data["profile"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        for route in ["profile", "favorites", "cart", "order-list"]:
            self.assertEqual(self.client.get(reverse(f"api:{route}")).status_code, 200)
        self.assertEqual(self.client.post(reverse("api:logout")).status_code, 204)
        self.assertFalse(Token.objects.filter(key=token).exists())
        self.assertEqual(self.client.get(reverse("api:profile")).status_code, 401)

    def test_wrong_password_and_inactive_account(self):
        url = reverse("api:login")
        self.assertEqual(self.client.post(url, {"username": self.buyer.username, "password": "wrong"}).status_code, 400)
        self.buyer.is_active = False
        self.buyer.save()
        self.assertEqual(self.client.post(url, {"username": self.buyer.username, "password": "test-mobile-password"}).status_code, 400)
        self.assertFalse(Token.objects.filter(user=self.buyer).exists())

    def test_profile_and_favorites_are_current_users(self):
        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.get(reverse("api:profile")).data["username"], self.buyer.username)
        self.assertEqual(self.client.get(reverse("api:favorites")).data["count"], 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(reverse("api:favorites")).data["count"], 0)

    def test_profile_patch_reuses_web_validation(self):
        self.client.force_authenticate(self.buyer)
        url = reverse("api:profile")
        self.assertEqual(self.client.patch(url, {"bio": "Suka barang preloved"}, format="json").status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Suka barang preloved")
        self.assertEqual(self.client.patch(url, {"student_id": "not-numeric"}).status_code, 400)

    def test_cart_isolation_and_server_calculated_total(self):
        self.client.force_authenticate(self.buyer)
        data = self.client.get(reverse("api:cart")).data
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["subtotal"], 90000)
        self.assertEqual(data["total_items"], 2)
        self.assertEqual(data["items"][0]["id"], self.item.pk)

    def test_unavailable_cart_item_excluded_from_subtotal(self):
        self.product.stock = 0
        self.product.save()
        self.client.force_authenticate(self.buyer)
        data = self.client.get(reverse("api:cart")).data
        self.assertEqual(data["subtotal"], 0)
        self.assertFalse(data["items"][0]["available"])
        self.assertTrue(data["items"][0]["unavailable_reason"])

    def test_empty_cart_without_creating_database_rows(self):
        self.client.force_authenticate(self.seller)
        data = self.client.get(reverse("api:cart")).data
        self.assertEqual(data, {"items": [], "subtotal": 0, "total_items": 0})
        self.assertFalse(Cart.objects.filter(user=self.seller).exists())

    def test_orders_scoped_to_buyer_or_seller(self):
        url = reverse("api:order-list")
        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.get(url).data["count"], 1)
        self.client.force_authenticate(self.seller)
        self.assertEqual(self.client.get(url).data["count"], 0)
        self.assertEqual(self.client.get(url, {"role": "seller"}).data["count"], 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(url, {"role": "seller"}).data["count"], 0)
        self.assertEqual(self.client.get(url, {"role": "invalid"}).status_code, 400)

    def test_other_buyer_cannot_read_invoice(self):
        url = reverse("api:order-detail", args=[self.order.pk])
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.get(url).data["items"][0]["product_name"], self.product.name)

    def test_staff_queue_checks_staff_role(self):
        url = reverse("api:order-list")
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(url, {"role": "staff"}).status_code, 403)
        self.other.is_staff = True
        self.other.save()
        self.assertEqual(self.client.get(url, {"role": "staff"}).data["count"], 1)

    def test_review_filter_and_private_mine(self):
        url = reverse("api:review-list")
        self.assertEqual(self.client.get(url, {"mine": "true"}).status_code, 401)
        self.client.force_authenticate(self.buyer)
        data = self.client.get(url, {"mine": "true", "product": self.product.pk}).data
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.review.pk)
        self.assertEqual(self.client.get(url, {"product": "bad"}).status_code, 400)

    def test_checkpoint_read_endpoints_reject_writes(self):
        self.client.force_authenticate(self.buyer)
        for route in ["product-list", "cart", "order-list", "review-list"]:
            self.assertEqual(self.client.post(reverse(f"api:{route}"), {}, format="json").status_code, 405)

    def test_session_writes_still_enforce_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.buyer.username, password="test-mobile-password"))
        self.assertEqual(client.patch(reverse("api:profile"), {"bio": "test"}).status_code, 403)
        token = Token.objects.create(user=self.buyer)
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(client.patch(reverse("api:profile"), {"bio": "test"}).status_code, 200)
