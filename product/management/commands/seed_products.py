import json
import random
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError


from product.models import Category, Product, ProductImage

DUMMYJSON_URL = "https://dummyjson.com/products?limit=60"
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

    def handle(self, *args, **options):
        with urlopen(Request(DUMMYJSON_URL, headers={"User-Agent": "Mozilla/5.0"})) as response:
            data = json.load(response)

        total = 0
        for item in data["products"]:
            category_name = item["category"].replace("-", " ").title()
            category, _ = Category.objects.get_or_create(name=category_name)

            price = round(item["price"] * DEFAULT_USD_RATE, -3)

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
                },
            )

            if created:
                for url in item["images"]:
                    ProductImage.objects.create(product=product, image_url=url)

            total += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed selesai: {total} produk"
            )
        )
