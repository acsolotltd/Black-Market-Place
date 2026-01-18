from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5})
        }


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=["image", "position"],
    extra=3,
    can_delete=True
)
