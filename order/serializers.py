from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "product_name", "seller_name", "thumbnail", "quantity", "unit_price", "line_total"]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    number = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    delivery_method_display = serializers.CharField(source="get_delivery_method_display", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "number", "status", "status_display", "delivery_method", "delivery_method_display",
                  "subtotal", "shipping_cost", "total", "payment_status", "tracking_number", "created_at", "items"]
        read_only_fields = fields
