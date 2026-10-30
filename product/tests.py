from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse

from product.forms import ProductForm
from product.models import Category, Product, ProductImage
from profiles.models import Favorite


class ProductModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="seller1", email="seller1@ui.ac.id")
        cls.category = Category.objects.create(name="Elektronik")

    def test_category_string_and_slug_generation(self):
        self.assertEqual(str(self.category), "Elektronik")
        self.assertEqual(self.category.slug, "elektronik")

    def test_product_model_methods(self):
        product = Product.objects.create(
            name="Laptop Bekas",
            seller=self.user,
            category=self.category,
            price=3500000,
            stock=2,
            condition="like_new",
            thumbnail="https://example.com/laptop.jpg",
        )
        self.assertEqual(str(product), "Laptop Bekas")
        self.assertEqual(product.slug, "laptop-bekas")
        self.assertEqual(product.price_display(), "Rp 3.500.000")
        self.assertFalse(product.is_sold_out())
        self.assertEqual(product.seller_name(), "seller1")
        self.assertEqual(product.main_image_url(), "https://example.com/laptop.jpg")

        product.stock = 0
        product.save()
        self.assertTrue(product.is_sold_out())

    def test_product_fallback_image(self):
        product = Product.objects.create(
            name="Meja Belajar",
            seller=self.user,
            category=self.category,
            price=150000,
            stock=1,
            thumbnail="",
        )
        img = ProductImage.objects.create(product=product, image_url="https://example.com/meja.jpg")
        self.assertEqual(product.main_image_url(), "https://example.com/meja.jpg")


class ProductFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Pakaian")

    def test_valid_product_form(self):
        form_data = {
            "name": "Jaket Kuning UI",
            "category": self.category.pk,
            "description": "Jaket makara asli kuning ukuran L",
            "price": 120000,
            "stock": 1,
            "condition": "good",
            "brand": "Makara",
            "weight_grams": 400,
            "thumbnail": "https://example.com/jaket.jpg",
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_form_allows_blank_category(self):
        form_data = {
            "name": "Barang Bebas",
            "description": "Tanpa kategori",
            "price": 50000,
            "stock": 1,
            "condition": "fair",
            "weight_grams": 300,
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())


class ProductViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(username="owner", email="owner@ui.ac.id", password="password123")
        cls.other_user = User.objects.create_user(username="other", email="other@ui.ac.id", password="password123")
        cls.category = Category.objects.create(name="Buku")
        cls.product = Product.objects.create(
            name="Kalkulator Saintifik",
            seller=cls.owner,
            category=cls.category,
            price=150000,
            stock=3,
            condition="like_new",
        )

    def test_product_list_view_and_filtering(self):
        response = self.client.get(reverse("product:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kalkulator Saintifik")

        # Filter by search
        res_search = self.client.get(reverse("product:index"), {"q": "Kalkulator"})
        self.assertContains(res_search, "Kalkulator Saintifik")

        # Filter by non-existing
        res_empty = self.client.get(reverse("product:index"), {"q": "NonExistentThing"})
        self.assertNotContains(res_empty, "Kalkulator Saintifik")

        # Filter by category
        res_cat = self.client.get(reverse("product:index"), {"category": self.category.slug})
        self.assertContains(res_cat, "Kalkulator Saintifik")

    def test_product_detail_view(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kalkulator Saintifik")
        self.assertContains(response, "Rp 150.000")

    def test_create_product_authenticated(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("product:create"), {
            "name": "Buku Diktat Kalkulus",
            "category": self.category.pk,
            "description": "Buku latihan kalkulus semester 1",
            "price": 45000,
            "stock": 1,
            "condition": "good",
            "weight_grams": 600,
        })
        self.assertRedirects(response, reverse("profile:index"))
        self.assertTrue(Product.objects.filter(name="Buku Diktat Kalkulus", seller=self.owner).exists())

    def test_create_product_anonymous_redirects(self):
        response = self.client.post(reverse("product:create"), {"name": "Test"})
        self.assertEqual(response.status_code, 302)

    def test_update_product_by_owner(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("product:update", args=[self.product.slug]), {
            "name": "Kalkulator Saintifik Casio",
            "category": self.category.pk,
            "description": "Kondisi mulus",
            "price": 175000,
            "stock": 2,
            "condition": "like_new",
            "weight_grams": 500,
        })
        self.assertRedirects(response, self.product.get_absolute_url())
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 175000)

    def test_update_product_by_non_owner_forbidden(self):
        self.client.force_login(self.other_user)
        response = self.client.post(reverse("product:update", args=[self.product.slug]), {
            "name": "Hacked Title",
            "category": self.category.pk,
            "price": 1000,
            "stock": 1,
            "condition": "good",
        })
        self.assertEqual(response.status_code, 403)

    def test_delete_product_by_non_owner_forbidden(self):
        self.client.force_login(self.other_user)
        response = self.client.post(reverse("product:delete", args=[self.product.slug]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_delete_product_by_owner(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("product:delete", args=[self.product.slug]))
        self.assertRedirects(response, reverse("product:index"))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
