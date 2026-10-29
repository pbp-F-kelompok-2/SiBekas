from django.contrib.auth import (
    get_user_model,
)
from django.test import TestCase
from django.urls import reverse

from product.models import (
    Category,
    Product,
)

from .models import (
    Cart,
    CartItem,
)


User = get_user_model()


class CartAjaxTests(TestCase):

    def setUp(self):
        self.user = (
            User.objects.create_user(
                username="ajaxbuyer",
                email="ajaxbuyer@ui.ac.id",
                password="testpass123",
            )
        )

        self.seller = (
            User.objects.create_user(
                username="ajaxseller",
                email="ajaxseller@ui.ac.id",
                password="testpass123",
            )
        )


        self.electronics = (
            Category.objects.create(
                name="Elektronik AJAX",
            )
        )

        self.books = (
            Category.objects.create(
                name="Buku AJAX",
            )
        )


        self.keyboard = (
            Product.objects.create(
                seller=self.seller,

                category=
                    self.electronics,

                name=
                    "Keyboard Filter Test",

                description=
                    "Keyboard untuk test.",

                price=350000,

                stock=5,

                condition="good",
            )
        )


        self.book = (
            Product.objects.create(
                seller=self.seller,

                category=
                    self.books,

                name=
                    "Novel Filter Test",

                description=
                    "Buku untuk test.",

                price=50000,

                stock=3,

                condition="good",
            )
        )


        self.cart = (
            Cart.objects.create(
                user=self.user,
            )
        )


        self.keyboard_item = (
            CartItem.objects.create(
                cart=self.cart,

                product=
                    self.keyboard,

                quantity=1,
            )
        )


        self.book_item = (
            CartItem.objects.create(
                cart=self.cart,

                product=
                    self.book,

                quantity=1,
            )
        )


        self.client.login(
            username="ajaxbuyer",
            password="testpass123",
        )


    def test_cart_json_requires_login(
        self
    ):
        self.client.logout()

        response = (
            self.client.get(
                reverse(
                    "cart:cart_json"
                )
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )


    def test_cart_json_returns_data(
        self
    ):
        response = (
            self.client.get(
                reverse(
                    "cart:cart_json"
                )
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )


        data = response.json()


        self.assertTrue(
            data["success"]
        )


        self.assertEqual(
            data["total_items"],
            2,
        )


        self.assertEqual(
            len(
                data["items"]
            ),
            2,
        )


        self.assertEqual(
            data["subtotal"],
            400000,
        )


    def test_category_filter(
        self
    ):
        response = (
            self.client.get(
                reverse(
                    "cart:index"
                ),
                {
                    "category":
                        self.electronics.slug,
                },
            )
        )


        self.assertContains(
            response,
            "Keyboard Filter Test",
        )


        self.assertNotContains(
            response,
            "Novel Filter Test",
        )


    def test_ajax_update_quantity(
        self
    ):
        response = (
            self.client.post(
                reverse(
                    "cart:update_item",
                    args=[
                        self.keyboard_item.id,
                    ],
                ),

                {
                    "action":
                        "increase",
                },

                HTTP_X_REQUESTED_WITH=
                    "XMLHttpRequest",
            )
        )


        self.assertEqual(
            response.status_code,
            200,
        )


        data = response.json()


        self.assertTrue(
            data["success"]
        )


        self.keyboard_item.refresh_from_db()


        self.assertEqual(
            self.keyboard_item.quantity,
            2,
        )


        self.assertEqual(
            data["cart_count"],
            3,
        )


        self.assertEqual(
            data["subtotal"],
            750000,
        )


    def test_ajax_remove_item(
        self
    ):
        response = (
            self.client.post(
                reverse(
                    "cart:remove_item",
                    args=[
                        self.keyboard_item.id,
                    ],
                ),

                {},

                HTTP_X_REQUESTED_WITH=
                    "XMLHttpRequest",
            )
        )


        self.assertEqual(
            response.status_code,
            200,
        )


        data = response.json()


        self.assertTrue(
            data["success"]
        )


        self.assertFalse(
            CartItem.objects
            .filter(
                pk=
                    self.keyboard_item.pk
            )
            .exists()
        )


        self.assertEqual(
            data["cart_count"],
            1,
        )


        self.assertEqual(
            data["subtotal"],
            50000,
        )

    def test_ajax_bulk_delete_selected(
        self
    ):
        response = self.client.post(
            reverse(
                "cart:bulk_delete"
            ),
            {
                "bulk_action":
                    "selected",

                "item_ids": [
                    self.keyboard_item.id,
                ],
            },
            HTTP_X_REQUESTED_WITH=
                "XMLHttpRequest",
        )


        self.assertEqual(
            response.status_code,
            200,
        )


        self.assertFalse(
            CartItem.objects
            .filter(
                pk=
                    self.keyboard_item.pk
            )
            .exists()
        )


        self.assertTrue(
            CartItem.objects
            .filter(
                pk=self.book_item.pk
            )
            .exists()
        )


        self.assertEqual(
            response.json()[
                "removed_count"
            ],
            1,
        )


    def test_ajax_bulk_delete_all(
        self
    ):
        response = self.client.post(
            reverse(
                "cart:bulk_delete"
            ),
            {
                "bulk_action":
                    "all",
            },
            HTTP_X_REQUESTED_WITH=
                "XMLHttpRequest",
        )


        self.assertEqual(
            response.status_code,
            200,
        )


        self.assertFalse(
            CartItem.objects
            .filter(
                cart=self.cart
            )
            .exists()
        )


        self.assertTrue(
            response.json()[
                "cart_empty"
            ]
        )

    def test_bulk_delete_cannot_delete_other_users_item(
        self
    ):
        other_user = (
            User.objects.create_user(
                username="other-buyer",
                password="testpass123",
            )
        )


        other_cart = (
            Cart.objects.create(
                user=other_user,
            )
        )


        other_item = (
            CartItem.objects.create(
                cart=other_cart,
                product=self.keyboard,
                quantity=1,
            )
        )


        response = self.client.post(
            reverse(
                "cart:bulk_delete"
            ),
            {
                "bulk_action":
                    "selected",

                "item_ids": [
                    other_item.id,
                ],
            },
            HTTP_X_REQUESTED_WITH=
                "XMLHttpRequest",
        )


        self.assertEqual(
            response.status_code,
            400,
        )


        self.assertTrue(
            CartItem.objects
            .filter(
                pk=other_item.pk
            )
            .exists()
        )