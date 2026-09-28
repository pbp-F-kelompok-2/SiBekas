from django.test import TestCase
from django.urls import reverse


class ProjectFoundationTests(TestCase):
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
