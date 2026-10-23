from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class CartMigrationTests(TransactionTestCase):
    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_references_are_preserved_and_aliases_are_merged(self):
        executor = MigrationExecutor(connection)
        old_target = [("cart", "0001_initial"), ("product", "0001_initial")]
        executor.migrate(old_target)
        old_apps = executor.loader.project_state(old_target).apps
        User = old_apps.get_model("auth", "User")
        Category = old_apps.get_model("product", "Category")
        Product = old_apps.get_model("product", "Product")
        Cart = old_apps.get_model("cart", "Cart")
        CartItem = old_apps.get_model("cart", "CartItem")
        user = User.objects.create(username="migration-buyer")
        category = Category.objects.create(name="Buku", slug="buku")
        product = Product.objects.create(name="Buku PBP", slug="buku-pbp", category=category, price=75000, stock=5)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product_reference=str(product.pk), quantity=1)
        CartItem.objects.create(cart=cart, product_reference="0" + str(product.pk), quantity=2)
        CartItem.objects.create(cart=cart, product_reference="missing-product", quantity=1)
        executor = MigrationExecutor(connection)
        new_target = [("cart", "0002_remove_cartitem_unique_product_per_cart_and_more")]
        executor.migrate(new_target)
        new_apps = executor.loader.project_state(new_target).apps
        items = new_apps.get_model("cart", "CartItem").objects.filter(cart_id=cart.pk)
        self.assertEqual(items.get(product_id=product.pk).quantity, 3)
        self.assertEqual(items.filter(product_id=None).count(), 1)
        self.assertEqual(items.count(), 2)
