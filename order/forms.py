import re

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator

from .models import Order


class PhoneNumberField(forms.CharField):
    def to_python(self, value):
        return re.sub(r"[\s()-]", "", super().to_python(value))


class CheckoutForm(forms.Form):
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
        choices=[(Order.DeliveryMethod.PICKUP, "Ambil di kampus UI (Gratis / Titik Temu)")],
        initial=Order.DeliveryMethod.PICKUP,
    )
    address = forms.CharField(
        label="Titik temu / alamat di kampus UI",
        max_length=1000,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "autocomplete": "street-address",
            "placeholder": "Contoh: Kantin Fasilkom UI, Perpustakaan Pusat UI, atau Gedung Kuliah",
        }),
    )
    payment_method = forms.ChoiceField(label="Metode pembayaran", choices=Order.PaymentMethod.choices)
    notes = forms.CharField(
        label="Catatan pesanan (opsional)",
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Pesan untuk penjual atau kesepakatan waktu temu"}),
    )
    checkout_token = forms.CharField(widget=forms.HiddenInput)
    shipping_quote = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.ORDER_ENABLE_DEMO_PAYMENT:
            self.fields["payment_method"].choices = [(Order.PaymentMethod.COD, Order.PaymentMethod.COD.label)]

    def clean(self):
        cleaned = super().clean()
        return cleaned
