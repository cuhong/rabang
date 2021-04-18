from ckeditor.widgets import CKEditorWidget
from django import forms

from product.models import Product
from show.models import Show


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'simple_description', 'thumbnail', 'description', 'original_price', 'delivery_type', 'delivery_fee',
            'sale_price'
        ]
        widgets = {
            'description': CKEditorWidget(),
        }


class ShowCreateForm(forms.ModelForm):
    class Meta:
        model = Show
        fields = [
            'title', 'title_display', 'description', 'poster', 'poster_video', 'start_at', 'end_at',
            'product'
        ]
        read_only_fields = ['id']
