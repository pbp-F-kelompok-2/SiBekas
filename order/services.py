import uuid

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from cart.models import Cart, CartItem
from cart.services import cart_summary
from product.models import Product

from .models import Order, OrderEvent, OrderItem
from .shipping import ShippingError, validate_quote


class OrderError(ValueError):
    pass


def checkout_token(user, summary):
    return signing.dumps({"user": user.pk, "fingerprint": summary["fingerprint"], "key": str(uuid.uuid4())}, salt="order.checkout")


def read_checkout_token(token, user):
    try:
        payload = signing.loads(token, salt="order.checkout", max_age=3600)
        if payload["user"] != user.pk:
            raise ValueError
        payload["key"] = uuid.UUID(payload["key"])
        return payload
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise OrderError("Sesi checkout kedaluwarsa. Muat ulang halaman checkout.") from exc


@transaction.atomic
def create_order(user, data):
    payload = read_checkout_token(data["checkout_token"], user)
    # Serializes checkout against this user's cart mutations and double submissions.
    cart = Cart.objects.select_for_update().filter(user=user).first()
    existing = Order.objects.filter(checkout_key=payload["key"], buyer=user).first()
    if existing:
        return existing
    if cart is None:
        raise OrderError("Keranjangmu masih kosong.")
    summary = cart_summary(user, lock=True)
    if not summary["available_items"] or summary["unavailable_items"]:
        raise OrderError("Periksa keranjang: hapus produk yang tidak tersedia atau sesuaikan jumlahnya.")
    if payload["fingerprint"] != summary["fingerprint"]:
        raise OrderError("Isi atau harga keranjang berubah. Muat ulang checkout untuk meninjau total terbaru.")
    if data["payment_method"] == Order.PaymentMethod.DEMO and not settings.ORDER_ENABLE_DEMO_PAYMENT:
        raise OrderError("Pembayaran simulasi tidak tersedia.")
    quote = {"cost": 0, "service": "Ambil di kampus UI", "etd": "Sesuai kesepakatan", "destination": "Kampus Universitas Indonesia", "destination_id": None}
    if data["delivery_method"] == Order.DeliveryMethod.COURIER:
        try:
            quote = validate_quote(data["shipping_quote"], summary, user.pk)
        except ShippingError as exc:
            raise OrderError(str(exc)) from exc
    order = Order.objects.create(
        checkout_key=payload["key"], buyer=user,
        recipient_name=data["recipient_name"], phone_number=data["phone_number"], address=data["address"],
        delivery_method=data["delivery_method"], destination=quote["destination"], destination_id=quote["destination_id"],
        shipping_service=quote["service"], shipping_etd=quote["etd"], shipping_cost=quote["cost"],
        subtotal=summary["subtotal"], total=summary["subtotal"] + quote["cost"], weight_grams=summary["weight_grams"],
        payment_method=data["payment_method"], notes=data.get("notes", ""),
        status=Order.Status.PROCESSING if data["payment_method"] == Order.PaymentMethod.COD else Order.Status.PENDING,
    )
    for row in summary["available_items"]:
        product = row["product"]
        # Conditional UPDATE also prevents overselling when SELECT FOR UPDATE is unavailable.
        changed = Product.objects.filter(pk=product.pk, stock__gte=row["quantity"]).update(stock=F("stock") - row["quantity"])
        if not changed:
            raise OrderError(f"Stok {product.name} berubah. Periksa keranjang kembali.")
        OrderItem.objects.create(
            order=order, product=product, seller_id=product.seller_id, product_name=product.name,
            seller_name=product.seller_name(), thumbnail=product.thumbnail, condition=product.get_condition_display(),
            unit_price=product.price, quantity=row["quantity"],
        )
    CartItem.objects.filter(cart=cart, pk__in=[row["id"] for row in summary["available_items"]]).delete()
    OrderEvent.objects.create(order=order, actor=user, status=order.status, description="Pesanan dibuat. Stok barang telah dicadangkan.")
    return order


@transaction.atomic
def change_status(order_id, actor, action, *, tracking_number=""):
    order = Order.objects.select_for_update().get(pk=order_id)
    is_buyer = order.buyer_id == actor.pk
    if not (is_buyer or actor.is_staff):
        raise OrderError("Kamu tidak memiliki akses ke pesanan ini.")
    now = timezone.now()
    if action == "pay":
        if not is_buyer or order.payment_method != Order.PaymentMethod.DEMO or not settings.ORDER_ENABLE_DEMO_PAYMENT or order.status != Order.Status.PENDING:
            raise OrderError("Pesanan ini tidak dapat dibayar melalui simulasi.")
        order.payment_status = Order.PaymentStatus.PAID
        order.paid_at = now
        order.status = Order.Status.PROCESSING
        description = "Pembayaran simulasi berhasil. Tidak ada uang yang ditransfer."
    elif action == "ship":
        if not actor.is_staff or order.status != Order.Status.PROCESSING:
            raise OrderError("Hanya petugas yang dapat menyiapkan pesanan yang sedang diproses.")
        tracking_number = tracking_number.strip()
        if order.delivery_method == Order.DeliveryMethod.COURIER and not tracking_number:
            raise OrderError("Nomor resi wajib diisi untuk pengiriman kurir.")
        if len(tracking_number) > 100:
            raise OrderError("Nomor resi maksimal 100 karakter.")
        order.tracking_number = tracking_number
        order.status = Order.Status.SHIPPED
        description = "Pesanan dikirim." if order.delivery_method == Order.DeliveryMethod.COURIER else "Pesanan siap diambil di titik temu."
    elif action == "complete":
        if not is_buyer or order.status != Order.Status.SHIPPED:
            raise OrderError("Konfirmasi hanya tersedia untuk pembeli setelah pesanan dikirim atau siap diambil.")
        order.status = Order.Status.COMPLETED
        order.completed_at = now
        if order.payment_method == Order.PaymentMethod.COD:
            order.payment_status = Order.PaymentStatus.PAID
            order.paid_at = now
        description = "Pembeli mengonfirmasi barang diterima dan pembayaran selesai."
    elif action == "cancel":
        if not order.can_cancel:
            raise OrderError("Pesanan yang sudah dikirim, selesai, atau dibatalkan tidak dapat dibatalkan lagi.")
        # Order row lock + terminal status ensures stock is restored exactly once.
        for item in order.items.order_by("product_id"):
            if item.product_id:
                Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
        order.status = Order.Status.CANCELLED
        order.cancelled_at = now
        if order.payment_status == Order.PaymentStatus.PAID:
            order.payment_status = Order.PaymentStatus.REFUNDED
        description = "Pesanan dibatalkan. Stok barang dikembalikan."
    else:
        raise OrderError("Perubahan status tidak valid.")
    order.save()
    OrderEvent.objects.create(order=order, actor=actor, status=order.status, description=description)
    return order
