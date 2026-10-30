"""Shared utility functions and security decorators for the SiBekas project."""

from functools import wraps
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


def format_rupiah(value):
    """Format an integer value as Indonesian Rupiah string.

    Example:
        >>> format_rupiah(150000)
        'Rp 150.000'
    """
    if value is None:
        return "Rp 0"
    return f"Rp {value:,}".replace(",", ".")


def rate_limit(limit=15, seconds=60):
    """Decorator untuk membatasi laju request (rate limiting) pada endpoint sensitif."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == "POST" and request.user.is_authenticated:
                key = f"rate:{view_func.__name__}:{request.user.pk}"
                cache.add(key, 0, seconds)
                if cache.incr(key) > limit:
                    messages.error(request, "Terlalu banyak permintaan. Silakan tunggu beberapa saat.")
                    return redirect("order:index")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def seller_required(view_func):
    """Memastikan hanya pemilik produk atau admin yang berhak mengedit/menghapus produk."""
    @wraps(view_func)
    def _wrapped_view(request, slug, *args, **kwargs):
        from product.models import Product
        product = get_object_or_404(Product, slug=slug)
        if product.seller != request.user and not request.user.is_superuser:
            raise PermissionDenied("Anda tidak memiliki izin untuk mengelola listing produk ini.")
        return view_func(request, slug, *args, **kwargs)
    return _wrapped_view


def order_participant_required(view_func):
    """Memastikan hanya pembeli, penjual produk terkait, atau staf yang dapat mengakses pesanan."""
    @wraps(view_func)
    def _wrapped_view(request, order_id, *args, **kwargs):
        from order.models import Order
        order = get_object_or_404(Order, pk=order_id)
        is_participant = (
            order.buyer_id == request.user.pk
            or order.items.filter(seller=request.user).exists()
            or request.user.is_staff
            or request.user.is_superuser
        )
        if not is_participant:
            raise PermissionDenied("Anda tidak memiliki izin untuk mengakses data transaksi pesanan ini.")
        return view_func(request, order_id, *args, **kwargs)
    return _wrapped_view
