from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Brand, BikeProduct, Customer, Sale


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    # 👇 DITO MO ILALAGAY
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs.update({
                'class': 'form-input'
            })


        


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-input'}),
        }


class BikeProductForm(forms.ModelForm):
    class Meta:
        model = BikeProduct
        fields = ['name', 'sku', 'category', 'brand', 'description', 'price', 'cost_price',
                  'stock_quantity', 'low_stock_threshold', 'condition', 'frame_size', 
                  'wheel_size', 'color', 'weight', 'image', 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., BIKE-001'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-input'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-input'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'frame_size': forms.TextInput(attrs={'class': 'form-input'}),
            'wheel_size': forms.TextInput(attrs={'class': 'form-input'}),
            'color': forms.TextInput(attrs={'class': 'form-input'}),
            'weight': forms.TextInput(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+63 XXX XXX XXXX'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        # Only show the fields the customer actually needs to change
        fields = ['quantity', 'payment_method', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }