from rest_framework import generics, serializers

from .models import Order
from .serializers import OrderSerializer


class OrderQuerySerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["buyer", "seller", "staff"], default="buyer")


class MyOrderListAPI(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        query = OrderQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        role = query.validated_data["role"]
        orders = Order.objects.prefetch_related("items")
        if role == "seller":
            orders = orders.filter(items__seller=self.request.user).distinct()
        elif role == "staff":
            from rest_framework.exceptions import PermissionDenied
            if not self.request.user.is_staff:
                raise PermissionDenied("Hanya petugas yang dapat melihat antrean kampus.")
        else:
            orders = orders.filter(buyer=self.request.user)
        return orders.order_by("-created_at", "-pk")


class MyOrderDetailAPI(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # A buyer sees their invoice. Seller/staff queues use the list endpoint.
        return Order.objects.filter(buyer=self.request.user).prefetch_related("items")
