from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from product.models import Product

from .models import Cart, CartItem
from .services import cart_summary


@login_required
def index(request):
    return render(request, "cart/index.html", cart_summary(request.user))


@require_POST
@login_required
def add_item(request):
    try:
        product_id = int(request.POST.get("product_id", ""))
        quantity = int(request.POST.get("quantity", "1"))
        if not 0 < product_id < 2**63 or not 0 < quantity <= 999:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, "Pilih produk dan jumlah yang valid.")
        return redirect("cart:index")
    with transaction.atomic():
        cart, _ = Cart.objects.get_or_create(user=request.user)
        Cart.objects.select_for_update().get(pk=cart.pk)
        product = get_object_or_404(Product, pk=product_id)
        item = cart.items.filter(product=product).first()
        new_quantity = quantity + (item.quantity if item else 0)
        if product.seller_id == request.user.pk:
            messages.error(request, "Kamu tidak dapat membeli produk milikmu sendiri.")
        elif new_quantity > product.stock:
            messages.error(request, "Jumlah barang melebihi stok yang tersedia.")
        else:
            if item:
                item.quantity = new_quantity
                item.save(update_fields=["quantity", "updated_at"])
            else:
                cart.items.create(product=product, quantity=quantity)
            messages.success(request, "Produk ditambahkan ke keranjang.")
    return redirect("cart:index")


@require_POST
@login_required
def update_item(request, item_id):
    with transaction.atomic():
        cart = get_object_or_404(Cart.objects.select_for_update(), user=request.user)
        item = get_object_or_404(CartItem.objects.select_for_update(), pk=item_id, cart=cart)
        product = item.product
        action = request.POST.get("action")
        quantity = item.quantity + (1 if action == "increase" else -1)
        if action not in {"increase", "decrease"} or quantity < 1:
            messages.error(request, "Jumlah minimal satu barang. Gunakan Hapus untuk mengeluarkannya.")
        elif product is None or quantity > product.stock:
            messages.error(request, "Jumlah barang melebihi stok yang tersedia.")
        else:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])
    return redirect("cart:index")


@require_POST
@login_required
def remove_item(request, item_id):
    with transaction.atomic():
        cart = get_object_or_404(Cart.objects.select_for_update(), user=request.user)
        item = get_object_or_404(CartItem.objects.select_for_update(), pk=item_id, cart=cart)
        item.delete()
    messages.success(request, "Produk dihapus dari keranjang.")
    return redirect("cart:index")
