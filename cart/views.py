from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from product.models import Category, Product

from .models import Cart, CartItem
from .services import cart_summary


def is_ajax(request):
    return (
        request.headers.get("X-Requested-With")
        == "XMLHttpRequest"
    )


def get_selected_category(request):
    return (
        request.GET.get("category")
        or request.POST.get("category")
        or ""
    ).strip()


def build_cart_context(user, category_slug=""):
    summary = cart_summary(user)

    categories = list(
        Category.objects
        .filter(
            products__cart_items__cart__user=user,
        )
        .distinct()
        .order_by("name")
    )

    if category_slug:
        visible_item_ids = set(
            CartItem.objects
            .filter(
                cart__user=user,
                product__category__slug=category_slug,
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        display_available_items = [
            item
            for item in summary["available_items"]
            if item["id"] in visible_item_ids
        ]

        display_unavailable_items = [
            item
            for item in summary["unavailable_items"]
            if item["id"] in visible_item_ids
        ]

    else:
        display_available_items = list(
            summary["available_items"]
        )

        display_unavailable_items = list(
            summary["unavailable_items"]
        )

    selected_category_name = next(
        (
            category.name
            for category in categories
            if category.slug == category_slug
        ),
        "",
    )

    summary.update(
        {
            "categories": categories,
            "selected_category": category_slug,
            "selected_category_name":
                selected_category_name,
            "cart_has_items": bool(
                summary["available_items"]
                or summary["unavailable_items"]
            ),
            "display_available_items":
                display_available_items,
            "display_unavailable_items":
                display_unavailable_items,
            "is_filtered": bool(
                category_slug
            ),
            "filter_has_results": bool(
                display_available_items
                or display_unavailable_items
            ),
        }
    )

    return summary


def cart_state_payload(user):
    summary = cart_summary(user)

    available_items = (
        summary["available_items"]
    )

    unavailable_items = (
        summary["unavailable_items"]
    )

    return {
        "cart_count":
            summary["total_items"],

        "subtotal":
            summary["subtotal"],

        "subtotal_display":
            summary["subtotal_display"],

        "available_count":
            len(available_items),

        "unavailable_count":
            len(unavailable_items),

        "cart_empty":
            not (
                available_items
                or unavailable_items
            ),

        "checkout_allowed":
            bool(
                available_items
                and not unavailable_items
            ),

        "checkout_url":
            reverse("order:checkout"),
    }


@login_required
def index(request):
    category_slug = (
        get_selected_category(request)
    )

    context = build_cart_context(
        request.user,
        category_slug,
    )

    return render(
        request,
        "cart/index.html",
        context,
    )


@require_GET
@login_required
def cart_json(request):
    category_slug = (
        get_selected_category(request)
    )

    context = build_cart_context(
        request.user,
        category_slug,
    )

    def serialize_item(item):
        product = item["product"]

        return {
            "id":
                item["id"],

            "product_id":
                (
                    product.pk
                    if product
                    else None
                ),

            "name":
                item["name"],

            "seller":
                item["seller"],

            "quantity":
                item["quantity"],

            "price":
                item["price"],

            "price_display":
                item["price_display"],

            "line_total_display":
                item["line_total_display"],

            "stock":
                item["stock"],

            "available":
                item["available"],

            "unavailable_reason":
                item["unavailable_reason"],
        }

    items = [
        serialize_item(item)
        for item in (
            context["display_available_items"]
            + context["display_unavailable_items"]
        )
    ]

    return JsonResponse(
        {
            "success": True,

            "selected_category":
                category_slug,

            "items":
                items,

            "total_items":
                context["total_items"],

            "subtotal":
                context["subtotal"],

            "subtotal_display":
                context["subtotal_display"],

            "available_count":
                len(
                    context[
                        "available_items"
                    ]
                ),

            "unavailable_count":
                len(
                    context[
                        "unavailable_items"
                    ]
                ),
        }
    )


@require_POST
@login_required
def add_item(request):
    try:
        product_id = int(
            request.POST.get(
                "product_id",
                "",
            )
        )

        quantity = int(
            request.POST.get(
                "quantity",
                "1",
            )
        )

        if (
            not 0 < product_id < 2**63
            or not 0 < quantity <= 999
        ):
            raise ValueError

    except (TypeError, ValueError):
        messages.error(
            request,
            "Pilih produk dan jumlah yang valid.",
        )

        return redirect(
            "cart:index"
        )

    with transaction.atomic():
        cart, _ = (
            Cart.objects.get_or_create(
                user=request.user,
            )
        )

        Cart.objects.select_for_update().get(
            pk=cart.pk,
        )

        product = get_object_or_404(
            Product,
            pk=product_id,
        )

        item = (
            cart.items
            .filter(
                product=product
            )
            .first()
        )

        new_quantity = (
            quantity
            + (
                item.quantity
                if item
                else 0
            )
        )

        if (
            product.seller_id
            == request.user.pk
        ):
            messages.error(
                request,
                "Kamu tidak dapat membeli "
                "produk milikmu sendiri.",
            )

        elif (
            new_quantity
            > product.stock
        ):
            messages.error(
                request,
                "Jumlah barang melebihi "
                "stok yang tersedia.",
            )

        else:
            if item:
                item.quantity = (
                    new_quantity
                )

                item.save(
                    update_fields=[
                        "quantity",
                        "updated_at",
                    ]
                )

            else:
                cart.items.create(
                    product=product,
                    quantity=quantity,
                )

            messages.success(
                request,
                "Produk ditambahkan "
                "ke keranjang.",
            )

    return redirect(
        "cart:index"
    )


@require_POST
@login_required
def update_item(
    request,
    item_id,
):
    error_message = ""

    with transaction.atomic():
        cart = get_object_or_404(
            Cart.objects
            .select_for_update(),

            user=request.user,
        )

        item = get_object_or_404(
            CartItem.objects
            .select_for_update(),

            pk=item_id,
            cart=cart,
        )

        product = item.product
        action = request.POST.get(
            "action"
        )

        if action not in {
            "increase",
            "decrease",
        }:
            error_message = (
                "Aksi perubahan jumlah "
                "tidak valid."
            )

        else:
            if action == "increase":
                quantity = (
                    item.quantity + 1
                )

            else:
                quantity = (
                    item.quantity - 1
                )

            if quantity < 1:
                error_message = (
                    "Jumlah minimal satu "
                    "barang. Gunakan Hapus "
                    "untuk mengeluarkannya."
                )

            elif (
                product is None
                or quantity
                > product.stock
            ):
                error_message = (
                    "Jumlah barang melebihi "
                    "stok yang tersedia."
                )

            else:
                item.quantity = quantity

                item.save(
                    update_fields=[
                        "quantity",
                        "updated_at",
                    ]
                )

    if error_message:
        if is_ajax(request):
            return JsonResponse(
                {
                    "success": False,
                    "message":
                        error_message,
                },
                status=400,
            )

        messages.error(
            request,
            error_message,
        )

        return redirect(
            "cart:index"
        )

    if is_ajax(request):
        payload = cart_state_payload(
            request.user
        )

        payload.update(
            {
                "success": True,

                "message":
                    "Jumlah barang "
                    "diperbarui.",

                "item_id":
                    item.pk,

                "quantity":
                    item.quantity,

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
            }
        )

        return JsonResponse(
            payload
        )

    return redirect(
        "cart:index"
    )


@require_POST
@login_required
def remove_item(
    request,
    item_id,
):
    with transaction.atomic():
        cart = get_object_or_404(
            Cart.objects
            .select_for_update(),

            user=request.user,
        )

        item = get_object_or_404(
            CartItem.objects
            .select_for_update(),

            pk=item_id,
            cart=cart,
        )

        removed_id = item.pk
        item.delete()

    if is_ajax(request):
        payload = cart_state_payload(
            request.user
        )

        payload.update(
            {
                "success": True,

                "message":
                    "Produk dihapus "
                    "dari keranjang.",

                "removed_id":
                    removed_id,
            }
        )

        return JsonResponse(
            payload
        )

    messages.success(
        request,
        "Produk dihapus dari keranjang.",
    )

    return redirect(
        "cart:index"
    )