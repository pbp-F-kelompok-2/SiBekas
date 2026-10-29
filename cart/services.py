import hashlib
import json

from sibekas.utils import format_rupiah

from product.models import Product

from .models import CartItem


def cart_summary(user, *, lock=False):
    """Shared cart/checkout snapshot using Rheza's Product foreign key."""
    items = CartItem.objects.filter(cart__user=user).order_by("pk")
    if lock:
        items = items.select_for_update()
    items = list(items)
    product_ids = [i.product_id for i in items if i.product_id]
    products = Product.objects.filter(pk__in=product_ids).order_by("pk")
    if lock:
        products = products.select_for_update()
    products = {p.pk: p for p in products}
    available, unavailable = [], []
    for item in items:
        product = products.get(item.product_id)
        reason = ""
        if product is None:
            reason = "Produk sudah tidak tersedia"
        elif product.seller_id == user.pk:
            reason = "Produk milikmu sendiri"
        elif product.stock < item.quantity:
            reason = "Barang sudah terjual" if not product.stock else f"Stok tersisa {product.stock}; kurangi jumlah barang."
        row = {
            "id": item.pk, "cart_item": item, "product": product,
            "name": product.name if product else "Produk tidak tersedia",
            "seller": product.seller_name() if product else "SiBekas",
            "price": product.price if product else 0, "quantity": item.quantity,
            "condition": product.get_condition_display() if product else "",
            "thumbnail": product.thumbnail if product else "",
            "url": product.get_absolute_url() if product else "",
            "stock": product.stock if product else 0,
            "max_reached": item.quantity >= product.stock if product else True,
            "available": not bool(reason),
            "unavailable_reason": reason,
            "price_display": format_rupiah(product.price) if product else "-",
            "line_total_display": format_rupiah(product.price * item.quantity) if product else "-",
        }
        (unavailable if reason else available).append(row)
    subtotal = sum(row["price"] * row["quantity"] for row in available)
    fingerprint = hashlib.sha256(json.dumps([
        [row["id"], row["product"].pk, row["quantity"], row["price"], row["product"].weight_grams, row["product"].seller_id]
        for row in available
    ]).encode()).hexdigest()
    return {
        "available_items": available, "unavailable_items": unavailable,
        "subtotal": subtotal, "subtotal_display": format_rupiah(subtotal),
        "total_items": sum(row["quantity"] for row in available),
        "weight_grams": sum(max(1, row["product"].weight_grams) * row["quantity"] for row in available),
        "fingerprint": fingerprint,
    }
