from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, connection
from django.db.migrations.executor import MigrationExecutor

from product.models import Product


class Command(BaseCommand):
    help = "Periksa database, migrasi, katalog produk DummyJSON, petugas, dan konfigurasi checkout tanpa mengubah data."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="Wajib minimal 50 produk dan satu petugas aktif.")
        parser.add_argument("--deployment", action="store_true", help="Wajib mode produksi dan pemeriksaan strict.")

    def handle(self, *args, **options):
        try:
            connection.ensure_connection()
            executor = MigrationExecutor(connection)
            pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if pending:
                raise CommandError("Masih ada migrasi tertunda. Jalankan python manage.py migrate terlebih dahulu.")
            products = Product.objects.count()
            staff = get_user_model().objects.filter(is_active=True, is_staff=True).count()
        except DatabaseError as exc:
            raise CommandError("Database belum siap. Periksa DATABASE_URL dan jalankan migrasi.") from exc

        self.stdout.write(self.style.SUCCESS("Database dan migrasi: siap."))
        problems = []
        strict = options["strict"] or options["deployment"]
        for ready, message in [
            (products >= 50, f"Katalog produk DummyJSON: {products} produk (target minimal 50)."),
            (staff > 0, f"Petugas aktif: {staff} (diperlukan untuk menyiapkan pesanan)."),
        ]:
            self.stdout.write(self.style.SUCCESS(message) if ready else self.style.WARNING(message))
            if not ready and strict:
                problems.append(message)

        if options["deployment"] and settings.DEBUG:
            problems.append("Deployment wajib menggunakan DJANGO_DEBUG=False.")
        if options["deployment"] and connection.vendor != "postgresql":
            problems.append("DATABASE_URL PostgreSQL persisten belum dikonfigurasi; database saat ini masih SQLite.")
        self.stdout.write("Pengiriman: Ambil di kampus UI (Gratis / COD / Demo).")
        self.stdout.write("Pembayaran: COD saat pengambilan" + (" dan simulasi akademik." if settings.ORDER_ENABLE_DEMO_PAYMENT else "."))
        if problems:
            raise CommandError("\n".join(problems))
        self.stdout.write(self.style.SUCCESS("Pemeriksaan selesai. Tidak ada data yang diubah."))
