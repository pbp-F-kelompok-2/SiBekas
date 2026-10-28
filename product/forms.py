
from django import forms
from .models import Product


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
            "price": forms.NumberInput(attrs={"min": 0}),
            "stock": forms.NumberInput(attrs={"min": 0}),
            "weight_grams": forms.NumberInput(attrs={"min": 0}),
            "thumbnail": forms.URLInput(
                attrs={"placeholder": "https://contoh.com/foto.jpg"}
            ),
        }
