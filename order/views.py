from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from cart.services import cart_summary
from profiles.models import Profile

from .forms import CheckoutForm
from .models import Order
from .services import OrderError, change_status, checkout_token, create_order, read_checkout_token


def accessible_orders(user):
    return Order.objects.all() if user.is_staff else Order.objects.filter(buyer=user)


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
        orders = orders.filter(Q(recipient_name__icontains=query) | Q(items__product_name__icontains=query)).distinct()
    page = Paginator(orders.prefetch_related("items"), 8).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "order/index.html", {
        "page_obj": page, "status_choices": Order.Status.choices, "active_status": status,
        "query": query, "manage": manage, "page_query": params.urlencode(),
    })


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    if request.method == "POST":
        # A retry after a successful checkout returns the original order, even with an empty cart.
        try:
            payload = read_checkout_token(request.POST.get("checkout_token", ""), request.user)
            existing = Order.objects.filter(checkout_key=payload["key"], buyer=request.user).first()
            if existing:
                return redirect(existing)
        except OrderError:
            pass
    summary = cart_summary(request.user)
    if not summary["available_items"] or summary["unavailable_items"]:
        messages.error(request, "Periksa keranjang terlebih dahulu. Pastikan barang tersedia dan jumlahnya sesuai stok.")
        return redirect("cart:index")
    profile = Profile.objects.filter(user=request.user).first()
    initial = {
        "recipient_name": profile.full_name if profile and profile.full_name else request.user.get_full_name() or request.user.username,
        "phone_number": profile.phone_number if profile else "",
        "address": profile.address if profile else "",
        "delivery_method": Order.DeliveryMethod.PICKUP,
        "payment_method": Order.PaymentMethod.COD,
        "checkout_token": checkout_token(request.user, summary),
    }
    form = CheckoutForm(request.POST if request.method == "POST" else None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            order = create_order(request.user, form.cleaned_data)
        except OrderError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Pesanan berhasil dibuat.")
            return redirect(order)
    return render(request, "order/checkout.html", {
        **summary, "form": form, "shipping_available": False,
        "demo_enabled": settings.ORDER_ENABLE_DEMO_PAYMENT, "selected_quote": None,
        "checkout_total": summary["subtotal"],
    })


@login_required
@require_GET
def detail(request, order_id):
    order = get_object_or_404(accessible_orders(request.user).prefetch_related("items__product", "events"), pk=order_id)
    return render(request, "order/detail.html", {"order": order, "is_buyer": order.buyer_id == request.user.pk, "demo_enabled": settings.ORDER_ENABLE_DEMO_PAYMENT})


@require_POST
@login_required
def update_status(request, order_id):
    order = get_object_or_404(accessible_orders(request.user), pk=order_id)
    try:
        change_status(order.pk, request.user, request.POST.get("action"), tracking_number=request.POST.get("tracking_number", ""))
    except OrderError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Status pesanan berhasil diperbarui.")
    return redirect(order)


@login_required
@require_GET
def destinations(request):
    return JsonResponse({"destinations": []})


@require_POST
@login_required
def shipping_quotes(request):
    summary = cart_summary(request.user)
    return JsonResponse({"quotes": [], "subtotal": summary["subtotal"]})
