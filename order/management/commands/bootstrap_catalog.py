from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from product.models import Product


class Command(BaseCommand):
    help = "Isi katalog awal pada release hanya jika DJANGO_SEED_INITIAL_PRODUCTS diaktifkan."

    def handle(self, *args, **options):
        if not settings.SEED_INITIAL_PRODUCTS:
            self.stdout.write("Pengisian katalog awal otomatis tidak diaktifkan.")
            return
        if Product.objects.count() >= 50:
            self.stdout.write("Katalog sudah memiliki minimal 50 produk; data tidak diubah.")
            return
        call_command("seed_products", skip_existing=True, stdout=self.stdout)
        if Product.objects.count() < 50:
            raise CommandError("Katalog belum mencapai 50 produk setelah seed. Periksa data Product sebelum melanjutkan deployment.")
