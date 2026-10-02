from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class ProjectFoundationTests(TestCase):
    def test_pws_deployment_host_is_allowed(self):
        response = self.client.get(
            reverse("home"),
            HTTP_HOST="faris-salman-sibekas.pws.cs.ui.ac.id",
        )

        self.assertEqual(response.status_code, 200)

    def test_homepage_is_available(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SiBekas")

    def test_health_check_includes_database(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok", "database": "ok"})

    def test_every_main_module_is_available(self):
        routes = (
            "product:index",
            "profile:index",
            "cart:index",
            "order:index",
            "review:index",
        )

        for route in routes:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)

User = get_user_model()


class SharedTemplateTests(TestCase):
    def test_home_uses_shared_navigation(self):
        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            "Beranda",
        )

        self.assertContains(
            response,
            "Produk",
        )

        self.assertContains(
            response,
            "Keranjang",
        )

        self.assertContains(
            response,
            "Pesanan",
        )

        self.assertContains(
            response,
            "Ulasan",
        )

        self.assertContains(
            response,
            "Profil",
        )

    def test_footer_is_rendered(self):
        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            "Barang lama, cerita baru.",
        )

    def test_guest_navigation_state(self):
        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            "Guest",
        )

        self.assertContains(
            response,
            "Masuk",
        )

    def test_authenticated_navigation_state(self):
        user = User.objects.create_user(
            username="rheza",
            password="testpass123",
        )

        self.client.force_login(
            user
        )

        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            "rheza",
        )

        self.assertNotContains(
            response,
            "Guest",
        )
