import hashlib
import json

from sibekas.utils import format_rupiah

from product.models import Product

from .models import CartItem


def cart_summary(
    user,
    *,
    item_ids=None,
    lock=False,
):
    """
    Build a cart snapshot.

    If item_ids is provided, only those CartItems
    belonging to the current user are included.
    """

    items = CartItem.objects.filter(
        cart__user=user
    )

    if item_ids is not None:
        items = items.filter(
            pk__in=item_ids
        )

    items = items.order_by(
        "pk"
    )

    if lock:
        items = items.select_for_update()

    items = list(items)


    product_ids = [
        item.product_id
        for item in items
        if item.product_id
    ]


    products = Product.objects.filter(
        pk__in=product_ids
    ).order_by(
        "pk"
    )


    if lock:
        products = (
            products.select_for_update()
        )


    products = {
        product.pk: product
        for product in products
    }


    available = []
    unavailable = []


    for item in items:
        product = products.get(
            item.product_id
        )

        reason = ""


        if product is None:
            reason = (
                "Produk sudah tidak tersedia"
            )

        elif (
            product.seller_id
            == user.pk
        ):
            reason = (
                "Produk milikmu sendiri"
            )

        elif (
            product.stock
            < item.quantity
        ):
            if not product.stock:
                reason = (
                    "Barang sudah terjual"
                )
            else:
                reason = (
                    f"Stok tersisa "
                    f"{product.stock}; "
                    "kurangi jumlah barang."
                )


        row = {
            "id":
                item.pk,

            "cart_item":
                item,

            "product":
                product,

            "name":
                (
                    product.name
                    if product
                    else "Produk tidak tersedia"
                ),

            "seller":
                (
                    product.seller_name()
                    if product
                    else "SiBekas"
                ),

            "price":
                (
                    product.price
                    if product
                    else 0
                ),

            "quantity":
                item.quantity,

            "condition":
                (
                    product
                    .get_condition_display()
                    if product
                    else ""
                ),

            "thumbnail":
                (
                    product.thumbnail
                    if product
                    else ""
                ),

            "url":
                (
                    product.get_absolute_url()
                    if product
                    else ""
                ),

            "stock":
                (
                    product.stock
                    if product
                    else 0
                ),

            "max_reached":
                (
                    item.quantity
                    >= product.stock
                    if product
                    else True
                ),

            "available":
                not bool(reason),

            "unavailable_reason":
                reason,

            "price_display":
                (
                    format_rupiah(
                        product.price
                    )
                    if product
                    else "-"
                ),

            "line_total_display":
                (
                    format_rupiah(
                        product.price
                        * item.quantity
                    )
                    if product
                    else "-"
                ),
        }


        if reason:
            unavailable.append(
                row
            )
        else:
            available.append(
                row
            )


    subtotal = sum(
        row["price"]
        * row["quantity"]
        for row in available
    )


    fingerprint_data = [
        [
            row["id"],
            row["product"].pk,
            row["quantity"],
            row["price"],
            row["product"].weight_grams,
            row["product"].seller_id,
        ]
        for row in available
    ]


    fingerprint = hashlib.sha256(
        json.dumps(
            fingerprint_data
        ).encode()
    ).hexdigest()


    total_items = sum(
        row["quantity"]
        for row in available
    )


    weight_grams = sum(
        max(
            1,
            row["product"].weight_grams,
        )
        * row["quantity"]
        for row in available
    )


    return {
        "available_items":
            available,

        "unavailable_items":
            unavailable,

        "subtotal":
            subtotal,

        "subtotal_display":
            format_rupiah(
                subtotal
            ),

        "total_items":
            total_items,

        "weight_grams":
            weight_grams,

        "fingerprint":
            fingerprint,
    }