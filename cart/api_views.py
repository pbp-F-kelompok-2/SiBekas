from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CartItem
from .serializers import CartItemSerializer
from .services import cart_summary


class MyCartAPI(APIView):
    def get(self, request):
        summary = cart_summary(request.user)
        items = CartItem.objects.filter(cart__user=request.user).select_related(
            "product__category", "product__seller"
        ).prefetch_related("product__images").order_by("pk")
        availability = {
            row["id"]: {"available": row["available"], "unavailable_reason": row["unavailable_reason"]}
            for row in summary["available_items"] + summary["unavailable_items"]
        }
        rows = [dict(row, **availability[row["id"]]) for row in CartItemSerializer(items, many=True).data]
        return Response({"items": rows, "subtotal": summary["subtotal"], "total_items": summary["total_items"]})
