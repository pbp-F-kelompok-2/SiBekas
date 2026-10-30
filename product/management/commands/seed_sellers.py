import json
from urllib.request import Request, urlopen

from django.contrib.auth import get_user_model
from urllib.error import URLError
from django.core.management.base import BaseCommand, CommandError

from product.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = "https://dummyjson.com/users?limit=60&select=username,email"
        try:
            with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as response:
                users = json.load(response)["users"]
        except (URLError, OSError, ValueError) as exc:
            raise CommandError("Data penjual DummyJSON tidak dapat dimuat. Coba lagi nanti.") from exc
        for product in Product.objects.filter(dummyjson_id__isnull=False):
            user = users[product.dummyjson_id % len(users)]
            seller, _ = get_user_model().objects.get_or_create(username=user["username"])
            if not seller.email:
                seller.email = user.get("email", "")
                seller.save()
            product.seller = seller
            product.save()