from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Product, Order, Review, Category
from .models import Order, Payment
from .models import CustomerQuery
class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.role = self.cleaned_data.get('role')
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
