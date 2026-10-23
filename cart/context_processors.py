from django.db.models import Sum

from .models import CartItem


def cart_count(request):
    if not request.user.is_authenticated:
        return {
            "cart_count": 0,
        }

    total = (
        CartItem.objects
        .filter(
            cart__user=request.user,
            product__stock__gt=0,
        )
        .aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )

    return {
        "cart_count": total,
    }