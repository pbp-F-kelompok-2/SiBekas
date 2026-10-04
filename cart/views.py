from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


def index(request):
    cart_items = [
        {
            "id": 1,
            "name": "Buku Dasar-Dasar Pemrograman Python",
            "seller": "Mahasiswa UI",
            "price": 75000,
            "quantity": 1,
            "available": True,
            "condition": "Bekas - Sangat Baik",
        },
        {
            "id": 2,
            "name": "Keyboard Mechanical",
            "seller": "Mahasiswa UI",
            "price": 350000,
            "quantity": 1,
            "available": True,
            "condition": "Bekas - Baik",
        },
        {
            "id": 3,
            "name": "Headphone Wireless",
            "seller": "Mahasiswa UI",
            "price": 250000,
            "quantity": 1,
            "available": False,
            "condition": "Bekas - Baik",
            "unavailable_reason": "Barang sudah terjual",
        },
    ]

    available_items = [
        item
        for item in cart_items
        if item["available"]
    ]

    unavailable_items = [
        item
        for item in cart_items
        if not item["available"]
    ]

    for item in cart_items:
        item["price_display"] = format_rupiah(
            item["price"]
        )

        item["line_total_display"] = format_rupiah(
            item["price"] * item["quantity"]
        )

    subtotal = sum(
        item["price"] * item["quantity"]
        for item in available_items
    )

    context = {
        "available_items": available_items,
        "unavailable_items": unavailable_items,
        "subtotal_display": format_rupiah(
            subtotal
        ),
        "total_items": sum(
            item["quantity"]
            for item in available_items
        ),
    }

    return render(
        request,
        "cart/index.html",
        context,
    )


@require_POST
def add_item(request):
    messages.info(
        request,
        "Fitur tambah barang akan dihubungkan ke model Product.",
    )

    return redirect("cart:index")


@require_POST
def update_item(request, item_id):
    messages.info(
        request,
        f"Update CartItem {item_id} masih berupa skeleton.",
    )

    return redirect("cart:index")


@require_POST
def remove_item(request, item_id):
    messages.info(
        request,
        f"CartItem {item_id} akan dihapus pada implementasi CRUD berikutnya.",
    )

    return redirect("cart:index")


@require_POST
def add_item(request):
    messages.info(
        request,
        "Fitur tambah barang akan dihubungkan ke model Product.",
    )

    return redirect("cart:index")


@require_POST
def update_item(request, item_id):
    messages.info(
        request,
        f"Update CartItem {item_id} masih berupa skeleton.",
    )

    return redirect("cart:index")


@require_POST
def remove_item(request, item_id):
    messages.info(
        request,
        f"CartItem {item_id} akan dihapus pada implementasi CRUD berikutnya.",
    )

    return redirect("cart:index")