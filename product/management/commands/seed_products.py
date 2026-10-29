import json
import random
from urllib.error import URLError
from urllib.request import Request, urlopen
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand, CommandError

from product.models import Category, Product, ProductImage

DUMMYJSON_URL = "https://dummyjson.com/products?limit=60"
DUMMYJSON_USERS_URL = "https://dummyjson.com/users?limit=60&select=username"
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


class Command(BaseCommand):
    help = "Seed produk awal dari DummyJSON (aman dijalankan berulang kali)."

    def add_arguments(self, parser):
        parser.add_argument("--skip-existing", action="store_true", help="Pertahankan stok dan perubahan produk yang sudah ada.")

    def handle(self, *args, **options):
        try:
            with urlopen(Request(DUMMYJSON_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as response:
                data = json.load(response)
            with urlopen(Request(DUMMYJSON_USERS_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as response:
                users = json.load(response)["users"]
            if not isinstance(data, dict) or not isinstance(data.get("products"), list):
                raise ValueError
        except (URLError, OSError, ValueError) as exc:
            raise CommandError("Data awal DummyJSON tidak dapat dimuat. Coba lagi setelah koneksi tersedia.") from exc

        total = 0
        skipped = 0
        for item in data["products"]:
            if options["skip_existing"] and Product.objects.filter(dummyjson_id=item["id"]).exists():
                skipped += 1
                continue
            cat_raw = str(item.get("category", "")).strip()
            category_name = CATEGORY_NAMES.get(cat_raw, cat_raw.replace("-", " ").title()) or "Lainnya"
            category, _ = Category.objects.get_or_create(name=category_name)

            price = round(item["price"] * DEFAULT_USD_RATE, -3)
            username = users[item["id"] % len(users)]["username"]
            seller, _ = get_user_model().objects.get_or_create(username=username)
            product, created = Product.objects.update_or_create(
                dummyjson_id=item["id"],
                defaults={
                    "category": category,
                    "name": item["title"],
                    "description": item["description"],
                    "price": max(int(price), 1000),
                    "stock": item["stock"],
                    "brand": item.get("brand") or "",
                    "thumbnail": item["thumbnail"],
                    "condition": random.choice(["like_new", "good", "fair"]),
                    "seller": seller,
                },
            )

            if created:
                for url in item.get("images", []):
                    ProductImage.objects.create(product=product, image_url=url)

            total += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed selesai: {total} produk diproses, {skipped} produk lama dipertahankan"
            )
        )
