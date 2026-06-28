from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "quantity", "min_stock", "price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full"}),
            "category": forms.Select(attrs={"class": "w-full"}),
            "quantity": forms.NumberInput(attrs={"class": "w-full"}),
            "min_stock": forms.NumberInput(attrs={"class": "w-full"}),
            "price": forms.NumberInput(attrs={"class": "w-full pl-7"}),
        }
