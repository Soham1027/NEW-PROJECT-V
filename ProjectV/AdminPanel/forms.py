from .models import *
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        ))
    password = forms.CharField(widget=forms.PasswordInput( attrs={"placeholder": "Password", "class": "form-control"}))
    # remember_me = forms.BooleanField(label='Remember Me', required=False)


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ['product_name', 'price', 'description', 'item_view', 'item_like', 'recently_viewed']

        # Define custom widgets for each field
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Price'
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
            'item_like': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'recently_viewed': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['product', 'color', 'size', 'quantity', 'image_file', 'video_story_file', 'item_discount']

        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Color'
            }),
            'size': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'image_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'video_story_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'item_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,  # To allow decimal values for discount
                'value': 0.00
            }),
        }