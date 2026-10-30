import json
import re

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator

from .models import Order


class PhoneNumberField(forms.CharField):
    def to_python(self, value):
        return re.sub(r"[\s()-]", "", super().to_python(value))


class CheckoutForm(forms.Form):
    DELIVERY_CHOICES = [
        (Order.DeliveryMethod.PICKUP, "Ambil di Kampus UI / COD (Ongkir Rp 0)"),
        (Order.DeliveryMethod.COURIER, "Kirim Lewat Sistem Kurir (Jasa Ongkir AgenWebsite API)"),
    ]

    recipient_name = forms.CharField(
        label="Nama penerima",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    phone_number = PhoneNumberField(
        label="Nomor telepon",
        max_length=20,
        validators=[RegexValidator(r"^\+?\d{9,15}$", "Gunakan 9–15 digit angka, misalnya 081234567890.")],
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel", "placeholder": "081234567890"}),
    )
    delivery_method = forms.ChoiceField(
        label="Metode penerimaan",
        choices=DELIVERY_CHOICES,
        initial=Order.DeliveryMethod.PICKUP,
    )
    destination_postal_code = forms.CharField(
        label="Kode pos / kota tujuan (khusus kurir)",
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "Contoh: 16424 (Depok) atau 10110 (Jakarta)",
            "autocomplete": "postal-code",
            "id": "destination-postal-code",
        }),
    )
    address = forms.CharField(
        label="Titik temu kampus atau alamat tujuan lengkap",
        max_length=1000,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "autocomplete": "street-address",
            "placeholder": "Contoh: Kantin Fasilkom UI, Halte Bikun, atau Jl. Margonda Raya No. 100",
        }),
    )
    payment_method = forms.ChoiceField(label="Metode pembayaran", choices=Order.PaymentMethod.choices)
    notes = forms.CharField(
        label="Catatan pesanan (opsional)",
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Pesan untuk penjual atau instruksi kurir"}),
    )
    checkout_token = forms.CharField(widget=forms.HiddenInput)
    shipping_quote = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.ORDER_ENABLE_DEMO_PAYMENT:
            self.fields["payment_method"].choices = [(Order.PaymentMethod.COD, Order.PaymentMethod.COD.label)]

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("delivery_method")
        if method == Order.DeliveryMethod.COURIER:
            postal_code = cleaned.get("destination_postal_code", "").strip()
            quote_raw = cleaned.get("shipping_quote", "").strip()
            if not postal_code and not quote_raw:
                self.add_error(
                    "destination_postal_code",
                    "Masukkan kode pos atau pilih lokasi tujuan untuk menghitung ongkir kurir.",
                )
        return cleaned
