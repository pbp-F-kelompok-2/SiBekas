import json
from urllib.request import Request, urlopen

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from product.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = "https://dummyjson.com/users?limit=60&select=username,email"
        with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as response:
            users = json.load(response)["users"]
        for product in Product.objects.filter(dummyjson_id__isnull=False):
            user = users[product.dummyjson_id % len(users)]
            seller, _ = get_user_model().objects.get_or_create(username=user["username"])
            if not seller.email:
                seller.email = user.get("email", "")
                seller.save()
            product.seller = seller
            product.save()