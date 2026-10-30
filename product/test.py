from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from product.forms import ProductForm
import json
from io import BytesIO, StringIO
from unittest.mock import patch
from django.core.management import call_command

# from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from product.models import Category, Product, ProductImage
# from profiles.models import Favorite


class ProductTest(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.seller = User.objects.create_user(username="penjual")
        self.other = User.objects.create_user(username="pembeli")
        self.category = Category.objects.create(name="Buku")
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Buku Kalkulus",
            description="Masih bagus",
            price=50000,
        )

    def test_category_model(self):
        self.assertEqual(str(self.category), "Buku")
        self.assertEqual(self.category.slug, "buku")

    def test_product_model(self):
        self.assertEqual(str(self.product), "Buku Kalkulus")
        self.assertEqual(self.product.slug, "buku-kalkulus")
        self.assertEqual(self.product.price_display(), "Rp 50.000")
        self.assertEqual(self.product.seller_name(), "penjual")
        self.assertFalse(self.product.is_sold_out())

    def test_duplicate_name_gets_unique_slug(self):
        twin = Product.objects.create(category=self.category, name="Buku Kalkulus", description="x", price=1000)
        self.assertEqual(twin.slug, "buku-kalkulus-2")

    def test_list_page(self):
        response = self.client.get(reverse("product:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "product/list.html")
        self.assertContains(response, "Buku Kalkulus")

    def test_nonexistent_product_returns_404(self):
        response = self.client.get("/products/tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_bulk_test_without_selection_shows_error(self):
        self.client.force_login(self.seller)
        response = self.client.post(reverse("product:bulk_delete"), {"ids":[]})
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn("Tidak ada produk yang dipilih", messages)

    def test_bulk_delete_show_count(self):
        self.client.force_login(self.seller)
        response = self.client.post(reverse("product:bulk_delete"), {"ids": [self.product.pk]})
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn("1 produk berhasil dihapus", messages)

    def test_403_mengubah(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("product:update", args = [self.product.slug]))
        self.assertContains(response, "mengubah", status_code = 403)
        self.assertContains(response, "Kembali ke produk", status_code = 403)

    def test_anonymous_mine(self):
        response = self.client.get(reverse("product:index"), {"mine": "1"})
        self.assertNotContains(response,"Hapus yang dipilih")
        self.assertNotContains(response, "Pilih semua")

    def test_seed_sellers_from_dummyjson(self):
        product = Product.objects.create(name="Mascara", description="x", price=1000, dummyjson_id=1)
        users = BytesIO(json.dumps({"users": [{"username": "emilys"}]}).encode())
        with patch("product.management.commands.seed_sellers.urlopen", return_value=users):
            call_command("seed_sellers")
        product.refresh_from_db()
        self.assertEqual(product.seller.username, "emilys")

    def test_category_list_is_cached(self):
        self.client.get(reverse("product:index"))
        Category.objects.create(name="Elektronik Langka")
        response = self.client.get(reverse("product:index"))
        self.assertNotContains(response, "Elektronik Langka")

    def test_broken_image_is_hidden(self):
        self.product.thumbnail = "https://contoh.com/a.jpg"
        self.product.save()
        response = self.client.get(reverse("product:index"))
        self.assertContains(response, 'onerror="this.remove()"')

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

    def test_seller_profile_is_public_without_private_data(self):
        self.owner.email = "penjual@ui.ac.id"
        self.owner.save()
        response = self.client.get(reverse("product:seller", args=[self.owner.username]))
        self.assertContains(response, "Kalkulator Saintifik")
        self.assertNotContains(response, "penjual@ui.ac.id")
        self.assertNotContains(response, "Hapus Akun")

    def test_detail_links_to_seller_profile(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, reverse("product:seller", args = [self.owner.username]))

    