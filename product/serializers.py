"""Public catalogue contract shared by the website and mobile client."""

from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller_name = serializers.CharField(read_only=True)
    condition_display = serializers.CharField(source="get_condition_display", read_only=True)
    image_url = serializers.CharField(source="main_image_url", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "price", "stock", "condition",
            "condition_display", "brand", "weight_grams", "image_url", "category",
            "seller_id", "seller_name", "created_at", "updated_at",
        ]
        read_only_fields = fields


class ProductFilterSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, max_length=200)
    category = serializers.SlugField(required=False)
    condition = serializers.ChoiceField(choices=Product.CONDITION_CHOICES, required=False)
    min_price = serializers.IntegerField(min_value=0, required=False)
    max_price = serializers.IntegerField(min_value=0, required=False)

    def validate(self, attrs):
        if attrs.get("min_price", 0) > attrs.get("max_price", float("inf")):
            raise serializers.ValidationError("Harga minimum melebihi harga maksimum.")
        return attrs
