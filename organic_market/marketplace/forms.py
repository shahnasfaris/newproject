from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Product, Order, Review, Category
from .models import Order, Payment
from .models import CustomerQuery
class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🚫 Remove admin from choices
        self.fields['role'].choices = [
            ('farmer', 'Farmer'),
            ('customer', 'Customer'),
        ]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'image']


class UpdateStockForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['price', 'stock']



class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter delivery address'
            }),
        }



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']  # use fields from your Review model

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method']
class CustomerQueryForm(forms.ModelForm):
    class Meta:
        model = CustomerQuery
        fields = ['name', 'email', 'message']
