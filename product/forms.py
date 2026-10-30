
from django import forms
from .models import Product
from django.utils.html import strip_tags

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "price",
            "stock",
            "condition",
            "brand",
            "weight_grams",
            "thumbnail",
        ]
        labels = {
            "name": "Nama produk",
            "description": "Deskripsi produk",
            "category" : "Kategori",
            "price": "Harga (Rp)",
            "stock": "Stok",
            "condition": "Kondisi barang",
            "brand": "Merek",
            "weight_grams": "Berat (gram)",
            "thumbnail": "URL foto produk",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": 1}),
            "stock": forms.NumberInput(attrs={"min": 0}),
            "weight_grams": forms.NumberInput(attrs={"min": 1}),
            "thumbnail": forms.URLInput(
                attrs={"placeholder": "https://contoh.com/foto.jpg"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = "block w-full py-[0.7rem] px-[0.85rem] border border-solid border-[var(--line)] rounded-[var(--radius-base)] bg-[var(--paper)] text-[var(--ink)] text-[0.875rem] focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-[var(--kiwi-300)] focus-visible:outline-offset-1 focus-visible:border-[var(--green)]"
        for field in self.fields.values():
            tall = isinstance(field.widget, forms.Textarea)
            field.widget.attrs["class"] = base + (" min-h-[140px] resize-y" if tall else " min-h-[var(--button-lg)]")

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 1:
            raise forms.ValidationError("Harga minimal Rp 1")
        return price

    def clean_weight_grams(self):
        weight = self.cleaned_data["weight_grams"]
        if weight < 1:
            raise forms.ValidationError("Berat minimal 1 gram")
        return weight

    def clean_name(self):
        return strip_tags(self.cleaned_data["name"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()
