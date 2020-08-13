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
        fields = ['last_name', 'first_name', 'username', 'email']


class ShippingAddressForm(forms.ModelForm):

    street_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '1234 Main St #101',
            'class': 'form-control address p-street-address p-extended-address'
        }),
        required=True,
        label="番地(アパート名/部屋番号等)"
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Los Angeles',
            'class': 'form-control address p-locality'
        }),
        required=True,
        label="市区町村"
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'CA',
            'class': 'form-control address p-region'
        }),
        required=True,
        label="都道府県"
    )

    zip = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control address p-postal-code'
        }),
        required=True,
        label="郵便番号(ハイフン抜きで記入下さい)"
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
            'class': 'form-control address p-street-address p-extended-address'
        }),
        required=True,
        label="番地(アパート名/部屋番号等)"
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Los Angeles',
            'class': 'form-control address p-locality'
        }),
        required=True,
        label="市区町村"
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'CA',
            'class': 'form-control address p-region'
        }),
        required=True,
        label="都道府県"
    )

    zip = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control address p-postal-code'
        }),
        required=True,
        label="郵便番号(ハイフン抜きで記入下さい)"
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


class PrimaryBillingAddressForm(forms.Form):

    list_stored_address = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        queryset=None,
        required=False,
        empty_label=None
    )

    def __init__(self, user, *args, **kwargs):
        super(PrimaryBillingAddressForm, self).__init__(*args, **kwargs)
        self.fields['list_stored_address'].queryset = BillingAddress.objects.filter(
            user=user)
