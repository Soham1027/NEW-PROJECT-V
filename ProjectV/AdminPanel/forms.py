from .models import *
from django import forms

class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        ))
    password = forms.CharField(widget=forms.PasswordInput( attrs={"placeholder": "Password", "class": "form-control"}))
    # remember_me = forms.BooleanField(label='Remember Me', required=False)



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'price', 'description', 'item_view', 'recently_viewed']

        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Price',
                'step': 0.01
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Description',
                'rows': 3
            }),
            'item_view': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'recently_viewed': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }


class ProductImagesForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ['product', 'image', 'is_default']

        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class ProductLikeForm(forms.ModelForm):
    class Meta:
        model = ProductLike
        fields = ['created_by_id', 'products', 'date_liked']

        widgets = {
            'created_by_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Enter Creator ID'
            }),
            'products': forms.Select(attrs={
                'class': 'form-control',
            }),
            'date_liked': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }


# class ProductVariantForm(forms.ModelForm):
#     class Meta:
#         model = ProductVariant
#         fields = ['product', 'color', 'size', 'quantity', 'item_discount']

#         widgets = {
#             'product': forms.Select(attrs={
#                 'class': 'form-control',
#             }),
#             'color': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter Product Color'
#             }),
#             'size': forms.Select(attrs={
#                 'class': 'form-control',
#             }),
#             'quantity': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': 0,
#                 'value': 0
#             }),
#             'item_discount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': 0,
#                 'step': 0.01,
#                 'value': 0.00
#             }),
#         }
