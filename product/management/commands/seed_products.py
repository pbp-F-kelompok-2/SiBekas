import json
from decimal import ROUND_HALF_UP, Decimal
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from product.models import Category, Product, ProductImage

DUMMYJSON_URL = "https://dummyjson.com/products"
DEFAULT_LIMIT = 50
DEFAULT_USD_RATE = 16_000

CATEGORY_NAMES = {
    "beauty": "Kecantikan",
    "fragrances": "Parfum",
    "furniture": "Furnitur",
    "groceries": "Bahan Makanan",
    "home-decoration": "Dekorasi Rumah",
    "kitchen-accessories": "Peralatan Dapur",
    "laptops": "Laptop",
    "mens-shirts": "Kemeja Pria",
    "mens-shoes": "Sepatu Pria",
    "mens-watches": "Jam Tangan Pria",
    "mobile-accessories": "Aksesori Ponsel",
    "motorcycle": "Motor",
    "skin-care": "Perawatan Kulit",
    "smartphones": "Ponsel",
    "sports-accessories": "Perlengkapan Olahraga",
    "sunglasses": "Kacamata Hitam",
    "tablets": "Tablet",
    "tops": "Atasan",
    "vehicle": "Kendaraan",
    "womens-bags": "Tas Wanita",
    "womens-dresses": "Gaun Wanita",
    "womens-jewellery": "Perhiasan Wanita",
    "womens-shoes": "Sepatu Wanita",
    "womens-watches": "Jam Tangan Wanita",
}

CONDITION_CYCLE = [
    Product.Condition.LIKE_NEW,
    Product.Condition.GOOD,
    Product.Condition.GOOD,
    Product.Condition.FAIR,
]


def usd_to_rupiah(usd_price, rate):
    rupiah = Decimal(str(usd_price)) * Decimal(rate)
    thousands = (rupiah / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return max(int(thousands) * 1000, 1000)


def category_name_for(slug):
    return CATEGORY_NAMES.get(slug, slug.replace("-", " ").title())


class Command(BaseCommand):
    help = "Seed produk awal dari DummyJSON (aman dijalankan berulang kali)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_LIMIT,
            help=f"Jumlah produk yang di-seed (default {DEFAULT_LIMIT}, minimal 50).",
        )
        parser.add_argument(
            "--exclude",
            default="",
            help="Slug kategori DummyJSON yang dilewati, dipisahkan koma (mis. groceries).",
        )
        parser.add_argument(
            "--usd-rate",
            type=int,
            default=DEFAULT_USD_RATE,
            help=f"Kurs USD ke Rupiah untuk konversi harga (default {DEFAULT_USD_RATE}).",
        )
        parser.add_argument(
            "--file",
            help="Baca respons DummyJSON dari file JSON lokal alih-alih dari internet.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=15,
            help="Batas waktu request HTTP dalam detik.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 50:
            raise CommandError("--limit minimal 50 sesuai kebutuhan data awal.")

        excluded = {slug.strip() for slug in options["exclude"].split(",") if slug.strip()}
        raw_products = self.load_products(options, fetch_all=bool(excluded))
        products = [item for item in raw_products if item.get("category") not in excluded]
        products = products[:limit]

        if len(products) < limit:
            raise CommandError(
                f"Hanya {len(products)} produk yang tersedia, kurang dari {limit}."
            )

        created, updated = self.save_products(products, options["usd_rate"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed selesai: {created} produk baru, {updated} produk diperbarui. "
                f"Total produk DummyJSON di database: "
                f"{Product.objects.filter(source=Product.Source.DUMMYJSON).count()}."
            )
        )

    def load_products(self, options, fetch_all):
        if options["file"]:
            try:
                with open(options["file"], encoding="utf-8") as handle:
                    payload = json.load(handle)
            except (OSError, json.JSONDecodeError) as error:
                raise CommandError(f"Gagal membaca file {options['file']}: {error}")
        else:
            limit = 0 if fetch_all else options["limit"]
            url = f"{DUMMYJSON_URL}?limit={limit}"
            self.stdout.write(f"Mengambil data dari {url} ...")
            request = Request(url, headers={"User-Agent": "SiBekas-Seeder/1.0"})
            try:
                with urlopen(request, timeout=options["timeout"]) as response:
                    payload = json.load(response)
            except (URLError, TimeoutError, json.JSONDecodeError) as error:
                raise CommandError(f"Gagal mengambil data DummyJSON: {error}")

        products = payload.get("products") if isinstance(payload, dict) else payload
        if not isinstance(products, list):
            raise CommandError("Format data DummyJSON tidak dikenali (key 'products' tidak ada).")
        return products

    @transaction.atomic
    def save_products(self, items, usd_rate):
        created_count = 0
        updated_count = 0
        categories = {}

        for item in items:
            category_slug = item.get("category") or "lainnya"
            if category_slug not in categories:
                categories[category_slug], _ = Category.objects.get_or_create(
                    slug=category_slug,
                    defaults={"name": category_name_for(category_slug)},
                )

            external_id = int(item["id"])
            weight_grams = max(int(item.get("weight") or 5), 1) * 100

            product, created = Product.objects.update_or_create(
                source=Product.Source.DUMMYJSON,
                external_id=external_id,
                defaults={
                    "category": categories[category_slug],
                    "name": item["title"][:200],
                    "description": item.get("description", ""),
                    "price": usd_to_rupiah(item.get("price", 0), usd_rate),
                    "stock": max(int(item.get("stock") or 0), 0),
                    "condition": CONDITION_CYCLE[external_id % len(CONDITION_CYCLE)],
                    "brand": (item.get("brand") or "")[:100],
                    "weight_grams": weight_grams,
                    "thumbnail_url": item.get("thumbnail", ""),
                    "is_active": True,
                },
            )

            product.images.all().delete()
            ProductImage.objects.bulk_create(
                ProductImage(
                    product=product,
                    image_url=url,
                    alt_text=f"{product.name} - gambar {position + 1}",
                    position=position,
                )
                for position, url in enumerate(item.get("images") or [])
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count