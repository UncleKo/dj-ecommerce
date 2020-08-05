from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from django.contrib.auth.models import User
from .models import ShippingAddress, BillingAddress


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Eメール")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
        # email = forms.EmailField(label="Eメール")

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        required=True,
        label="名",
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        required=True,
        label="姓",
    )

    email = forms.EmailField(
        label="Eメール",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name', 'first_name']


class ShippingAddressForm(forms.ModelForm):

    street_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '1234 Main St #101',
            'class': 'form-control address'
        }),
        required=False
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Los Angeles',
            'class': 'form-control address'
        }),
        required=False
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'CA',
            'class': 'form-control address'
        }),
        required=False
    )

    zip = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control address'
        }),
        required=False
    )

    # country = CountryField(
    #     blank_label='(select country)').formfield(
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100 address'
    #     }),
    #     required=False
    # )

    # primary = forms.BooleanField(required=False)

    class Meta:
        model = ShippingAddress
        fields = ['street_address', 'city',
                  'state', 'zip']


class PrimaryShippingAddressForm(forms.Form):

    list_stored_address = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        # queryset=ShippingAddress.objects.all(),
        queryset=None,
        required=False,
        empty_label=None
    )

    def __init__(self, user, *args, **kwargs):
        super(PrimaryShippingAddressForm, self).__init__(*args, **kwargs)
        self.fields['list_stored_address'].queryset = ShippingAddress.objects.filter(
            user=user)


class BillingAddressForm(forms.ModelForm):

    street_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '1234 Main St #101',
            'class': 'form-control address'
        }),
        required=False
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Los Angeles',
            'class': 'form-control address'
        }),
        required=False
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'CA',
            'class': 'form-control address'
        }),
        required=False
    )

    zip = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control address'
        }),
        required=False
    )

    # country = CountryField(
    #     blank_label='(select country)').formfield(
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100 address'
    #     }),
    #     required=False
    # )

    # primary = forms.BooleanField(required=False)

    class Meta:
        model = BillingAddress
        fields = ['street_address', 'city',
                  'state', 'zip']
