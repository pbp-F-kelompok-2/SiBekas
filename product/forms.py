from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "description", "price", "stock", "condition", "brand", "weight_grams"]
    image = forms.ImageField(label = "Foto", required = False)
        