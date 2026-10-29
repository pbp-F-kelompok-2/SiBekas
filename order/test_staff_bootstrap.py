from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings


@override_settings(ORDER_STAFF_USERNAME="petugas-test", ORDER_STAFF_EMAIL="petugas-test@ui.ac.id", ORDER_STAFF_PASSWORD="Test-Only-Random-Password-2026!")
class StaffBootstrapTests(TestCase):
    def test_creates_staff_without_superuser_access_or_password_in_output(self):
        output = StringIO()
        call_command("bootstrap_order_staff", stdout=output)
        user = get_user_model().objects.get(username="petugas-test")
        self.assertTrue(user.is_active and user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("Test-Only-Random-Password-2026!"))
        self.assertNotIn("Test-Only-Random-Password-2026!", output.getvalue())

    def test_repeated_release_preserves_existing_password(self):
        call_command("bootstrap_order_staff", stdout=StringIO())
        with override_settings(ORDER_STAFF_PASSWORD="A-Different-Test-Password-2026!"):
            call_command("bootstrap_order_staff", stdout=StringIO())
        user = get_user_model().objects.get(username="petugas-test")
        self.assertTrue(user.check_password("Test-Only-Random-Password-2026!"))

    def test_does_not_promote_or_reset_existing_customer(self):
        user = get_user_model().objects.create_user(username="petugas-test", email="customer@ui.ac.id", password="Customer-Test-Password-2026!")
        with self.assertRaises(CommandError):
            call_command("bootstrap_order_staff", stdout=StringIO())
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("Customer-Test-Password-2026!"))

    @override_settings(ORDER_STAFF_PASSWORD="")
    def test_incomplete_configuration_does_not_create_user(self):
        with self.assertRaises(CommandError):
            call_command("bootstrap_order_staff", stdout=StringIO())
        self.assertFalse(get_user_model().objects.exists())

    def test_deployment_check_reports_missing_persistent_postgres(self):
        from django.db import connection

        if connection.vendor != "sqlite":
            self.skipTest("Checks the SQLite development fallback.")
        with self.assertRaisesMessage(CommandError, "PostgreSQL persisten belum dikonfigurasi"):
            call_command("check_order_readiness", deployment=True, stdout=StringIO())
