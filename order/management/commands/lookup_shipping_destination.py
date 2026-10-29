from django.core.management.base import BaseCommand, CommandError

from order.shipping import ShippingError, get_destinations


class Command(BaseCommand):
    help = "Cari ID lokasi RajaOngkir untuk konfigurasi asal pengiriman, tanpa menampilkan API key."

    def add_arguments(self, parser):
        parser.add_argument("query", nargs="+", help="Nama kelurahan, kecamatan, atau kode pos.")

    def handle(self, *args, **options):
        query = " ".join(options["query"]).strip()
        if not 3 <= len(query) <= 100:
            raise CommandError("Masukkan 3-100 karakter lokasi atau kode pos.")
        try:
            rows = get_destinations(query)
        except ShippingError as exc:
            raise CommandError(str(exc)) from exc
        if not rows:
            raise CommandError("Lokasi tidak ditemukan. Coba nama kelurahan atau kode pos lain.")
        for row in rows:
            self.stdout.write(f"{row['id']}\t{row['label']}")
        self.stdout.write("Pilih lokasi asal yang benar, lalu isi ID-nya sebagai RAJAONGKIR_ORIGIN_ID.")
