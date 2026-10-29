from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email


class Command(BaseCommand):
    help = "Buat petugas pesanan dari environment privat tanpa memberi hak superuser atau mereset akun lama."

    def handle(self, *args, **options):
        username = settings.ORDER_STAFF_USERNAME
        email = settings.ORDER_STAFF_EMAIL
        password = settings.ORDER_STAFF_PASSWORD
        if not any((username, email, password)):
            self.stdout.write("Pembuatan petugas otomatis tidak dikonfigurasi.")
            return
        if not all((username, email, password)):
            raise CommandError("Lengkapi ORDER_STAFF_USERNAME, ORDER_STAFF_EMAIL, dan ORDER_STAFF_PASSWORD pada environment privat.")
        users = get_user_model()
        existing = users.objects.filter(username=username).first()
        if existing:
            if not existing.is_active or not existing.is_staff or existing.email.casefold() != email.casefold():
                raise CommandError("Username petugas sudah dipakai akun lain atau tidak aktif. Akun yang ada tidak diubah.")
            self.stdout.write("Petugas sudah tersedia; password dan hak akses tidak diubah.")
            return
        if users.objects.filter(email__iexact=email).exists():
            raise CommandError("Email petugas sudah digunakan. Akun yang ada tidak diubah.")
        user = users(username=username, email=email, is_active=True, is_staff=True, is_superuser=False)
        try:
            user.full_clean(exclude=["password"])
            validate_email(email)
            validate_password(password, user)
        except ValidationError as exc:
            raise CommandError("Data atau password petugas tidak memenuhi validasi Django.") from exc
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS("Petugas pesanan dibuat. Akun tidak memiliki hak superuser; password tidak ditampilkan."))
