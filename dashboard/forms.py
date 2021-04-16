from ckeditor.widgets import CKEditorWidget
from django import forms

from product.models import Product


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'simple_description', 'thumbnail', 'description', 'options', 'original_price', 'delivery_type', 'delivery_fee',
            'sale_price'
        ]
        widgets = {
            'description': CKEditorWidget(),
        }