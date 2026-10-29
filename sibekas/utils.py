"""Shared utility functions and security decorators for the SiBekas project."""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def format_rupiah(value):
    """Format an integer value as Indonesian Rupiah string.

    Example:
        >>> format_rupiah(150000)
        'Rp 150.000'
    """
    if value is None:
        return "Rp 0"
    return f"Rp {value:,}".replace(",", ".")


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
    """Memastikan hanya pembeli atau staf yang dapat mengakses pesanan terkait."""
    @wraps(view_func)
    def _wrapped_view(request, order_id, *args, **kwargs):
        from order.models import Order
        order = get_object_or_404(Order, pk=order_id)
        if order.buyer != request.user and not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied("Anda tidak memiliki akses ke data transaksi ini.")
        return view_func(request, order_id, *args, **kwargs)
    return _wrapped_view
