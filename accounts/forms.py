from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from core.forms import BootstrapFormMixin
from customers.models import Customer
from .models import User


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class CustomerSignupForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        user.phone = self.cleaned_data["phone"]
        user.save()
        Customer.objects.create(
            user=user,
            name=user.get_full_name() or user.username,
            email=user.email,
            phone=user.phone,
        )
        return user
