import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from cart.services import cart_summary
from product.models import Product
from profiles.models import Profile

from .forms import CheckoutForm
from .models import Order
from .services import OrderError, change_status, checkout_token, create_order, read_checkout_token
from .shipping import get_shipping_quotes, search_destinations


def accessible_orders(user):
    if user.is_staff:
        return Order.objects.all()
    return Order.objects.filter(Q(buyer=user) | Q(items__seller=user)).distinct()


@login_required
@require_GET
def index(request):
    manage = request.user.is_staff and request.GET.get("view") == "manage"
    orders = accessible_orders(request.user) if manage else Order.objects.filter(buyer=request.user)
    status = request.GET.get("status", "")
    if status in Order.Status.values:
        orders = orders.filter(status=status)
    else:
        status = ""
    query = request.GET.get("q", "").strip()[:100]
    if query:
        orders = orders.filter(
            Q(recipient_name__icontains=query) | Q(items__product_name__icontains=query)
        ).distinct()
    page = Paginator(orders.prefetch_related("items"), 8).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "order/index.html",
        {
            "page_obj": page,
            "status_choices": Order.Status.choices,
            "active_status": status,
            "query": query,
            "manage": manage,
            "page_query": params.urlencode(),
        },
    )


def parse_selected_item_ids(values):
    item_ids = []
    for value in values[:200]:
        try:
            item_id = int(value)
        except (TypeError, ValueError):
            continue
        if item_id > 0 and item_id not in item_ids:
            item_ids.append(item_id)
    return item_ids


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    selected_item_ids = None
    token_payload = None
    if request.method == "POST":
        try:
            token_payload = read_checkout_token(request.POST.get("checkout_token", ""), request.user)
            existing = Order.objects.filter(checkout_key=token_payload["key"], buyer=request.user).first()
            if existing:
                return redirect(existing)
            selected_item_ids = token_payload.get("item_ids")
        except OrderError:
            token_payload = None
    else:
        requested_values = request.GET.getlist("item")
        selection_requested = "item" in request.GET
        if selection_requested:
            selected_item_ids = parse_selected_item_ids(requested_values)
            if not selected_item_ids:
                messages.error(request, "Pilih minimal satu barang untuk checkout.")
                return redirect("cart:index")

    summary = cart_summary(request.user, item_ids=selected_item_ids)

    if request.method == "GET" and selected_item_ids is not None:
        valid_selected_ids = [
            row["id"]
            for row in (summary["available_items"] + summary["unavailable_items"])
        ]
        if not valid_selected_ids:
            messages.error(request, "Barang yang dipilih tidak ditemukan di keranjangmu.")
            return redirect("cart:index")
        selected_item_ids = valid_selected_ids
        summary = cart_summary(request.user, item_ids=selected_item_ids)

    if not summary["available_items"] or summary["unavailable_items"]:
        messages.error(
            request,
            "Periksa keranjang terlebih dahulu. Pastikan barang tersedia dan jumlahnya sesuai stok.",
        )
        return redirect("cart:index")

    profile = Profile.objects.filter(user=request.user).first()
    initial_postal = "16424"

    initial = {
        "recipient_name": (
            profile.full_name
            if (profile and profile.full_name)
            else (request.user.get_full_name() or request.user.username)
        ),
        "phone_number": profile.phone_number if profile else "",
        "address": profile.address if profile else "",
        "destination_postal_code": initial_postal,
        "delivery_method": Order.DeliveryMethod.PICKUP,
        "payment_method": Order.PaymentMethod.COD,
        "checkout_token": checkout_token(request.user, summary, item_ids=selected_item_ids),
    }

    form = CheckoutForm(
        request.POST if request.method == "POST" else None,
        initial=initial,
    )

    if request.method == "POST" and form.is_valid():
        try:
            order = create_order(request.user, form.cleaned_data)
        except OrderError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Pesanan berhasil dibuat.")
            return redirect(order)

    # Initial courier rates for UI Depok area (fallback / cache ready)
    initial_quotes = get_shipping_quotes(initial_postal, summary["weight_grams"])

    return render(
        request,
        "order/checkout.html",
        {
            **summary,
            "form": form,
            "shipping_available": True,
            "demo_enabled": settings.ORDER_ENABLE_DEMO_PAYMENT,
            "initial_quotes": initial_quotes,
            "selected_quote": None,
            "checkout_total": summary["subtotal"],
        },
    )


@login_required
@require_GET
def detail(request, order_id):
    order = get_object_or_404(
        accessible_orders(request.user).prefetch_related("items__product", "events"),
        pk=order_id,
    )
    is_buyer = order.buyer_id == request.user.pk
    is_seller = order.items.filter(seller=request.user).exists()
    return render(
        request,
        "order/detail.html",
        {
            "order": order,
            "is_buyer": is_buyer,
            "is_seller": is_seller,
            "demo_enabled": settings.ORDER_ENABLE_DEMO_PAYMENT,
        },
    )


@require_POST
@login_required
def update_status(request, order_id):
    order = get_object_or_404(accessible_orders(request.user), pk=order_id)
    try:
        change_status(
            order.pk,
            request.user,
            request.POST.get("action"),
            tracking_number=request.POST.get("tracking_number", ""),
        )
    except OrderError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Status pesanan berhasil diperbarui.")
    return redirect(order)


@login_required
@require_GET
def destinations(request):
    query = request.GET.get("q", "").strip()[:50]
    results = search_destinations(query)
    return JsonResponse({"destinations": results})


@require_POST
@login_required
def shipping_quotes(request):
    summary = cart_summary(request.user)
    postal_code = request.POST.get("postal_code", "").strip()
    if not postal_code:
        try:
            body_data = json.loads(request.body.decode("utf-8"))
            postal_code = str(body_data.get("postal_code", "")).strip()
        except Exception:
            pass

    postal_code = postal_code or "16424"
    quotes = get_shipping_quotes(postal_code, summary["weight_grams"])
    return JsonResponse({
        "quotes": quotes,
        "subtotal": summary["subtotal"],
        "weight_grams": summary["weight_grams"],
        "postal_code": postal_code,
    })


@login_required
@require_GET
def seller_dashboard(request):
    """
    Halaman Penjual:
    1. Barang yang sedang ingin dijual (active products with stock > 0)
    2. Barang yang sedang di-checkout pembeli (orders in pending/processing/shipped)
    3. Riwayat Penjualan (completed orders where buyer completed the transaction)
    """
    selling_products = Product.objects.filter(
        seller=request.user, stock__gt=0
    ).select_related("category")

    in_checkout_orders = (
        Order.objects.filter(
            items__seller=request.user,
            status__in=[Order.Status.PENDING, Order.Status.PROCESSING, Order.Status.SHIPPED],
        )
        .distinct()
        .prefetch_related("items__product", "buyer", "events")
    )

    completed_orders = (
        Order.objects.filter(
            items__seller=request.user,
            status=Order.Status.COMPLETED,
        )
        .distinct()
        .prefetch_related("items__product", "buyer")
    )

    sold_out_products = Product.objects.filter(
        seller=request.user, stock=0
    ).select_related("category")

    total_revenue = sum(
        item.line_total
        for order in completed_orders
        for item in order.items.all()
        if item.seller_id == request.user.pk
    )

    return render(
        request,
        "order/seller_dashboard.html",
        {
            "selling_products": selling_products,
            "in_checkout_orders": in_checkout_orders,
            "completed_orders": completed_orders,
            "sold_out_products": sold_out_products,
            "total_selling": selling_products.count(),
            "total_in_checkout": in_checkout_orders.count(),
            "total_completed": completed_orders.count(),
            "total_revenue": total_revenue,
        },
    )
