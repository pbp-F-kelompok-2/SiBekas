from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from order.models import Order, OrderItem
from product.models import Category, Product
from review.forms import ReviewForm
from review.models import Review


class ReviewModelAndFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="reviewer1", email="rev1@ui.ac.id")
        cls.seller = User.objects.create_user(username="seller1", email="seller1@ui.ac.id")
        cls.category = Category.objects.create(name="Alat Tulis")
        cls.product = Product.objects.create(
            name="Penggaris Segitiga",
            seller=cls.seller,
            category=cls.category,
            price=15000,
            stock=5,
        )

    def test_review_creation_and_string(self):
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment="Sangat bagus dan presisi!",
        )
        self.assertEqual(str(review), f"reviewer1 - Penggaris Segitiga (5/5)")
        self.assertFalse(review.edited)

    def test_unique_review_per_user_product(self):
        Review.objects.create(user=self.user, product=self.product, rating=4, comment="Bagus")
        with self.assertRaises(IntegrityError):
            Review.objects.create(user=self.user, product=self.product, rating=5, comment="Duplikat")

    def test_review_form_valid(self):
        form = ReviewForm(data={"rating": 4, "comment": "Barang sesuai deskripsi."})
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        form_zero = ReviewForm(data={"rating": 0, "comment": "Kualitas buruk"})
        self.assertFalse(form_zero.is_valid())
        self.assertIn("rating", form_zero.errors)

        form_high = ReviewForm(data={"rating": 6, "comment": "Luar biasa"})
        self.assertFalse(form_high.is_valid())
        self.assertIn("rating", form_high.errors)

    def test_review_form_comment_max_length_validation(self):
        long_comment = "A" * 501
        form = ReviewForm(data={"rating": 5, "comment": long_comment})
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    def test_review_form_empty_comment(self):
        form = ReviewForm(data={"rating": 5, "comment": "   "})
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)


class ReviewViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(username="buyer_rev", email="buyer_rev@ui.ac.id", password="password123")
        self.other = User.objects.create_user(username="other_rev", email="other_rev@ui.ac.id", password="password123")
        self.seller = User.objects.create_user(username="seller_rev", email="seller_rev@ui.ac.id")
        self.category = Category.objects.create(name="Buku Kuliah")
        self.product = Product.objects.create(
            name="Buku Algoritma dan Struktur Data",
            seller=self.seller,
            category=self.category,
            price=80000,
            stock=2,
        )

        self.completed_order = Order.objects.create(
            checkout_key="11111111-1111-1111-1111-111111111111",
            buyer=self.buyer,
            recipient_name="Buyer Rev",
            phone_number="081234567890",
            address="Fasilkom UI",
            delivery_method="pickup",
            shipping_service="Ambil di kampus UI",
            shipping_cost=0,
            subtotal=80000,
            total=80000,
            weight_grams=500,
            payment_method="cod",
            payment_status="paid",
            status=Order.Status.COMPLETED,
        )
        self.order_item = OrderItem.objects.create(
            order=self.completed_order,
            product=self.product,
            seller=self.seller,
            product_name=self.product.name,
            seller_name=self.seller.username,
            thumbnail="",
            condition="Baik",
            unit_price=80000,
            quantity=1,
        )
        self.client.force_login(self.buyer)

    def test_review_index_view(self):
        response = self.client.get(reverse("review:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buku Algoritma dan Struktur Data")

    def test_create_review_for_completed_purchase(self):
        response = self.client.post(reverse("review:create", args=[self.product.pk]), {
            "rating": 5,
            "comment": "Buku sangat bersih dan lengkap catatannya!",
        })
        self.assertRedirects(response, reverse("review:index"))
        review = Review.objects.get(product=self.product, user=self.buyer)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Buku sangat bersih dan lengkap catatannya!")

    def test_create_duplicate_review_redirects(self):
        Review.objects.create(user=self.buyer, product=self.product, rating=5, comment="Review 1")
        response = self.client.post(reverse("review:create", args=[self.product.pk]), {
            "rating": 4,
            "comment": "Review 2",
        })
        self.assertRedirects(response, reverse("review:index"))
        self.assertEqual(Review.objects.count(), 1)

    def test_cannot_review_unpurchased_product(self):
        unpurchased_product = Product.objects.create(
            name="Barang Lain",
            seller=self.seller,
            category=self.category,
            price=20000,
            stock=1,
        )
        response = self.client.get(reverse("review:create", args=[unpurchased_product.pk]))
        self.assertEqual(response.status_code, 404)

    def test_update_review_by_owner(self):
        review = Review.objects.create(user=self.buyer, product=self.product, rating=4, comment="Awal")
        response = self.client.post(reverse("review:update", args=[review.pk]), {
            "rating": 5,
            "comment": "Revisi: Ternyata sangat recommended!",
        })
        self.assertRedirects(response, reverse("review:index"))
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.edited)

    def test_update_review_by_non_owner_forbidden(self):
        review = Review.objects.create(user=self.buyer, product=self.product, rating=4, comment="Awal")
        self.client.force_login(self.other)
        response = self.client.post(reverse("review:update", args=[review.pk]), {
            "rating": 1,
            "comment": "Diubah oleh orang lain",
        })
        self.assertEqual(response.status_code, 403)

    def test_delete_review_by_non_owner_forbidden(self):
        review = Review.objects.create(user=self.buyer, product=self.product, rating=4, comment="Awal")
        self.client.force_login(self.other)
        response = self.client.post(reverse("review:delete", args=[review.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_delete_review_by_owner(self):
        review = Review.objects.create(user=self.buyer, product=self.product, rating=4, comment="Awal")
        response = self.client.post(reverse("review:delete", args=[review.pk]))
        self.assertRedirects(response, reverse("review:index"))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
