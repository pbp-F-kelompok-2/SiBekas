from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from product.forms import ProductForm
from product.models import Category, Product


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

    def test_anonymus_mine(self):
        response = self.client.get(reverse("product:index"), {"mine": "1"})
        self.assertNotContains(response,"Hapus yang dipilih")
        self.assertNotContains(response, "Pilih semua")