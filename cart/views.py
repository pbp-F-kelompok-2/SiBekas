from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from product.models import Product

from .models import Cart, CartItem


def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


@login_required
def index(request):
    cart, _ = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = (
        cart.items
        .select_related(
            "product",
            "product__seller",
        )
        .all()
    )

    available_items = []
    unavailable_items = []

    subtotal = 0
    total_items = 0

    for cart_item in cart_items:
        product = cart_item.product

        if product is None:
            continue

        available = product.stock > 0

        item = {
            "id": cart_item.id,
            "name": product.name,
            "url": product.get_absolute_url(),
            "seller": product.seller_name(),
            "price": product.price,
            "price_display": format_rupiah(
                product.price
            ),
            "quantity": cart_item.quantity,
            "stock": product.stock,
            "condition":
                product.get_condition_display(),
            "thumbnail": product.thumbnail,
            "line_total_display":
                format_rupiah(
                    product.price
                    * cart_item.quantity
                ),
            "available": available,
            "max_reached":
                cart_item.quantity
                >= product.stock,
        }

        if available:
            available_items.append(
                item
            )

            subtotal += (
                product.price
                * cart_item.quantity
            )

            total_items += (
                cart_item.quantity
            )

        else:
            item[
                "unavailable_reason"
            ] = "Barang sudah terjual"

            unavailable_items.append(
                item
            )

    context = {
        "available_items":
            available_items,

        "unavailable_items":
            unavailable_items,

        "subtotal_display":
            format_rupiah(subtotal),

        "total_items":
            total_items,
    }

    return render(
        request,
        "cart/index.html",
        context,
    )


@login_required
@require_POST
def add_item(request):
    product_id = request.POST.get(
        "product_id"
    )

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    if product.stock < 1:
        messages.error(
            request,
            "Produk sudah habis."
        )

        return redirect(
            product.get_absolute_url()
        )

    if (
        product.seller_id
        and product.seller_id
        == request.user.id
    ):
        messages.error(
            request,
            "Kamu tidak dapat membeli produk milikmu sendiri."
        )

        return redirect(
            product.get_absolute_url()
        )

    cart, _ = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = (
        CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": 1
            },
        )
    )

    if not created:
        if (
            cart_item.quantity
            >= product.stock
        ):
            messages.warning(
                request,
                "Jumlah produk di keranjang sudah mencapai stok maksimum."
            )

        else:
            cart_item.quantity += 1

            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Jumlah produk di keranjang ditambahkan."
            )

    else:
        messages.success(
            request,
            "Produk berhasil ditambahkan ke keranjang."
        )

    return redirect(
        "cart:index"
    )


@login_required
@require_POST
def update_item(
    request,
    item_id,
):
    cart_item = get_object_or_404(
        CartItem.objects.select_related(
            "product",
        ),
        id=item_id,
        cart__user=request.user,
    )

    action = request.POST.get(
        "action"
    )

    if action == "increase":
        if (
            cart_item.product
            and cart_item.quantity
            < cart_item.product.stock
        ):
            cart_item.quantity += 1

            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

        else:
            messages.warning(
                request,
                "Jumlah sudah mencapai stok maksimum."
            )

    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1

            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

    return redirect(
        "cart:index"
    )


@login_required
@require_POST
def remove_item(
    request,
    item_id,
):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    cart_item.delete()

    messages.success(
        request,
        "Produk dihapus dari keranjang."
    )

    return redirect(
        "cart:index"
    )