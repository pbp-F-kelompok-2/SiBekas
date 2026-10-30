import json
import uuid

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from cart.models import Cart, CartItem
from cart.services import cart_summary
from product.models import Product

from .forms import CheckoutForm
from .models import Order, OrderEvent, OrderItem
from .shipping import DEFAULT_QUOTES, get_shipping_quotes


class OrderError(ValueError):
    pass


def checkout_token(user, summary, item_ids=None):
    return signing.dumps(
        {
            "user": user.pk,
            "fingerprint": summary["fingerprint"],
            "key": str(uuid.uuid4()),
            "item_ids": (sorted(item_ids) if item_ids is not None else None),
        },
        salt="order.checkout",
    )


def read_checkout_token(token, user):
    try:
        payload = signing.loads(token, salt="order.checkout", max_age=3600)
        if payload["user"] != user.pk:
            raise ValueError
        payload["key"] = uuid.UUID(payload["key"])
        return payload
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise OrderError(
            "Sesi checkout kedaluwarsa. Muat ulang halaman checkout."
        ) from exc


@transaction.atomic
def create_order(user, data):
    payload = read_checkout_token(data.get("checkout_token", ""), user)
    # Serializes checkout against this user's cart mutations and double submissions.
    cart = Cart.objects.select_for_update().filter(user=user).first()
    existing = Order.objects.filter(checkout_key=payload["key"], buyer=user).first()
    if existing:
        return existing
    form = CheckoutForm(data)
    if not form.is_valid():
        errors = [str(error) for messages in form.errors.values() for error in messages]
        raise OrderError(" ".join(errors))
    data = form.cleaned_data
    if cart is None:
        raise OrderError("Keranjangmu masih kosong.")
    selected_item_ids = payload.get("item_ids")
    summary = cart_summary(user, item_ids=selected_item_ids, lock=True)
    if not summary["available_items"] or summary["unavailable_items"]:
        raise OrderError(
            "Periksa keranjang: hapus produk yang tidak tersedia atau sesuaikan jumlahnya."
        )
    if payload["fingerprint"] != summary["fingerprint"]:
        raise OrderError(
            "Isi atau harga keranjang berubah. Muat ulang checkout untuk meninjau total terbaru."
        )

    delivery_method = data.get("delivery_method", Order.DeliveryMethod.PICKUP)
    if delivery_method == Order.DeliveryMethod.COURIER:
        quote_data = None
        raw_quote = data.get("shipping_quote", "")
        if raw_quote:
            try:
                quote_data = json.loads(raw_quote)
            except Exception:
                quote_data = None

        postal_code = str(data.get("destination_postal_code") or "").strip()
        if not quote_data and postal_code:
            quotes = get_shipping_quotes(postal_code, summary["weight_grams"])
            if quotes:
                quote_data = quotes[0]

        if not quote_data:
            quote_data = DEFAULT_QUOTES[0]

        courier_name = quote_data.get("courier", "Kurir")
        service_name = quote_data.get("service", "Reguler")
        shipping_cost = int(quote_data.get("cost", 9000))
        shipping_service = f"{courier_name} - {service_name}"
        shipping_etd = str(quote_data.get("etd", "1-3 hari"))
        destination_label = postal_code or data.get("address") or "Pengiriman Kurir"
        destination_id_val = int(postal_code) if postal_code.isdigit() else None
    else:
        shipping_cost = 0
        shipping_service = "Ambil di kampus UI (COD)"
        shipping_etd = "Sesuai kesepakatan"
        destination_label = data.get("address") or "Kampus Universitas Indonesia"
        destination_id_val = None

    order = Order.objects.create(
        checkout_key=payload["key"],
        buyer=user,
        recipient_name=data["recipient_name"],
        phone_number=data["phone_number"],
        address=data["address"],
        delivery_method=delivery_method,
        destination=destination_label,
        destination_id=destination_id_val,
        shipping_service=shipping_service,
        shipping_etd=shipping_etd,
        shipping_cost=shipping_cost,
        subtotal=summary["subtotal"],
        total=summary["subtotal"] + shipping_cost,
        weight_grams=summary["weight_grams"],
        payment_method=data["payment_method"],
        notes=data.get("notes", ""),
        status=(
            Order.Status.PROCESSING
            if data["payment_method"] == Order.PaymentMethod.COD
            else Order.Status.PENDING
        ),
    )
    for row in summary["available_items"]:
        product = row["product"]
        # Conditional UPDATE also prevents overselling when SELECT FOR UPDATE is unavailable.
        changed = Product.objects.filter(
            pk=product.pk, stock__gte=row["quantity"]
        ).update(stock=F("stock") - row["quantity"])
        if not changed:
            raise OrderError(f"Stok {product.name} berubah. Periksa keranjang kembali.")
        OrderItem.objects.create(
            order=order,
            product=product,
            seller_id=product.seller_id,
            product_name=product.name,
            seller_name=product.seller_name(),
            thumbnail=product.thumbnail,
            condition=product.get_condition_display(),
            unit_price=product.price,
            quantity=row["quantity"],
        )
    CartItem.objects.filter(
        cart=cart, pk__in=[row["id"] for row in summary["available_items"]]
    ).delete()
    OrderEvent.objects.create(
        order=order,
        actor=user,
        status=order.status,
        description="Pesanan dibuat oleh pembeli. Stok barang telah dicadangkan.",
    )
    return order


@transaction.atomic
def change_status(order_id, actor, action, *, tracking_number=""):
    order = Order.objects.select_for_update().get(pk=order_id)
    is_buyer = order.buyer_id == actor.pk
    is_seller = order.items.filter(seller=actor).exists()
    is_staff = actor.is_staff

    if not (is_buyer or is_seller or is_staff):
        raise OrderError("Kamu tidak memiliki akses ke pesanan ini.")

    now = timezone.now()
    if action == "pay":
        if (
            not is_buyer
            or order.payment_method != Order.PaymentMethod.DEMO
            or not settings.ORDER_ENABLE_DEMO_PAYMENT
            or order.status != Order.Status.PENDING
        ):
            raise OrderError("Pesanan ini tidak dapat dibayar melalui simulasi.")
        order.payment_status = Order.PaymentStatus.PAID
        order.paid_at = now
        order.status = Order.Status.PROCESSING
        description = "Pembayaran simulasi berhasil. Tidak ada uang yang ditransfer."
    elif action == "ship":
        if not (is_seller or is_staff) or order.status != Order.Status.PROCESSING:
            raise OrderError(
                "Penjual atau petugas dapat mengirimkan / menyiapkan pesanan yang sedang diproses."
            )
        tracking_number = tracking_number.strip()
        if len(tracking_number) > 100:
            raise OrderError("Nomor resi atau catatan maksimal 100 karakter.")
        order.tracking_number = tracking_number
        order.status = Order.Status.SHIPPED
        if order.delivery_method == Order.DeliveryMethod.COURIER:
            resi_desc = f" Resi: {tracking_number}." if tracking_number else ""
            description = f"Barang telah dikirim melalui kurir.{resi_desc}"
        else:
            description = "Barang siap diserahterimakan di titik temu kampus UI."
    elif action == "complete":
        if not is_buyer or order.status != Order.Status.SHIPPED:
            raise OrderError(
                "Konfirmasi penerimaan hanya dapat dilakukan setelah akun pengirim (penjual/petugas) mengirimkan barang atau menandainya siap diambil."
            )
        order.status = Order.Status.COMPLETED
        order.completed_at = now
        if order.payment_method == Order.PaymentMethod.COD:
            order.payment_status = Order.PaymentStatus.PAID
            order.paid_at = now
        description = "Pembeli menyelesaikan transaksi dan mengonfirmasi barang telah diterima. Transaksi masuk ke riwayat penjualan."
    elif action == "cancel":
        if not order.can_cancel:
            raise OrderError(
                "Pesanan yang sudah dikirim, selesai, atau dibatalkan tidak dapat dibatalkan lagi."
            )
        # Order row lock + terminal status ensures stock is restored exactly once.
        for item in order.items.order_by("product_id"):
            if item.product_id:
                Product.objects.filter(pk=item.product_id).update(
                    stock=F("stock") + item.quantity
                )
        order.status = Order.Status.CANCELLED
        order.cancelled_at = now
        if order.payment_status == Order.PaymentStatus.PAID:
            order.payment_status = Order.PaymentStatus.REFUNDED
        description = "Pesanan dibatalkan. Stok barang dikembalikan ke penjual."
    else:
        raise OrderError("Perubahan status tidak valid.")

    order.save()
    OrderEvent.objects.create(
        order=order, actor=actor, status=order.status, description=description
    )
    return order
