from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from product.models import Category, Product

from .models import Cart, CartItem


User = get_user_model()


class CartTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rheza",
            email="rheza@ui.ac.id",
            password="testpass123",
        )

        self.seller = User.objects.create_user(
            username="seller",
            email="seller@ui.ac.id",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Elektronik",
        )

        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Keyboard Mechanical",
            description="Keyboard preloved.",
            price=350000,
            stock=5,
            condition="good",
        )

        self.cart = Cart.objects.create(
            user=self.user,
        )


class CartModelTests(CartTestBase):
    def test_user_has_one_cart(self):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                Cart.objects.create(
                    user=self.user,
                )

    def test_cart_item_can_be_created(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        self.assertEqual(
            item.cart,
            self.cart,
        )

        self.assertEqual(
            item.product,
            self.product,
        )

        self.assertEqual(
            item.quantity,
            1,
        )

    def test_same_product_cannot_be_duplicated(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CartItem.objects.create(
                    cart=self.cart,
                    product=self.product,
                    quantity=1,
                )

    def test_quantity_cannot_be_zero(self):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CartItem.objects.create(
                    cart=self.cart,
                    product=self.product,
                    quantity=0,
                )

    def test_line_total(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        self.assertEqual(
            item.line_total,
            700000,
        )


class CartViewTests(CartTestBase):
    def setUp(self):
        super().setUp()

        self.client.login(
            username="rheza",
            password="testpass123",
        )

    def test_cart_page_uses_expected_template(self):
        response = self.client.get(
            reverse("cart:index")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "cart/index.html",
        )

    def test_cart_page_displays_real_product(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.get(
            reverse("cart:index")
        )

        self.assertContains(
            response,
            "Keyboard Mechanical",
        )

        self.assertContains(
            response,
            "Rp 350.000",
        )

    def test_cart_page_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse("cart:index")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            reverse("profile:login"),
            response.url,
        )

    def test_add_item_creates_cart_item(self):
        response = self.client.post(
            reverse("cart:add_item"),
            {
                "product_id":
                    self.product.id,
            },
        )

        self.assertRedirects(
            response,
            reverse("cart:index"),
        )

        item = CartItem.objects.get(
            cart=self.cart,
            product=self.product,
        )

        self.assertEqual(
            item.quantity,
            1,
        )

    def test_add_same_product_increases_quantity(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        self.client.post(
            reverse("cart:add_item"),
            {
                "product_id":
                    self.product.id,
            },
        )

        item = CartItem.objects.get(
            cart=self.cart,
            product=self.product,
        )

        self.assertEqual(
            item.quantity,
            2,
        )

    def test_add_does_not_exceed_stock(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=5,
        )

        self.client.post(
            reverse("cart:add_item"),
            {
                "product_id":
                    self.product.id,
            },
        )

        item = CartItem.objects.get(
            cart=self.cart,
            product=self.product,
        )

        self.assertEqual(
            item.quantity,
            5,
        )

    def test_increase_quantity(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        self.client.post(
            reverse(
                "cart:update_item",
                args=[item.id],
            ),
            {
                "action": "increase",
            },
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            2,
        )

    def test_decrease_quantity(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        self.client.post(
            reverse(
                "cart:update_item",
                args=[item.id],
            ),
            {
                "action": "decrease",
            },
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            1,
        )

    def test_quantity_never_goes_below_one(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        self.client.post(
            reverse(
                "cart:update_item",
                args=[item.id],
            ),
            {
                "action": "decrease",
            },
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            1,
        )

    def test_remove_item(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.post(
            reverse(
                "cart:remove_item",
                args=[item.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("cart:index"),
        )

        self.assertFalse(
            CartItem.objects.filter(
                id=item.id
            ).exists()
        )

    def test_sold_out_product_is_unavailable(self):
        self.product.stock = 0
        self.product.save(
            update_fields=["stock"]
        )

        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.get(
            reverse("cart:index")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Sebagian barang tidak lagi tersedia",
        )

        self.assertContains(
            response,
            self.product.name,
        )

        self.assertContains(
            response,
            "0 barang",
        )

        self.assertContains(
            response,
            "Rp 0",
        )

    def test_user_cannot_modify_other_users_cart(self):
        other_user = User.objects.create_user(
            username="other",
            password="testpass123",
        )

        other_cart = Cart.objects.create(
            user=other_user,
        )

        item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.post(
            reverse(
                "cart:update_item",
                args=[item.id],
            ),
            {
                "action": "increase",
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )