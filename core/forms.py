from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import PAYMENT_CHOICES, DELIVERY_TIME
from users.models import ShippingAddress, BillingAddress


BILLING_ADDRESS_OPTION = (
    ('A', 'この住所を使う'),
    ('B', '請求先住所を配送先住所と同じにする')
)


class CheckoutForm(forms.Form):

    delivery_time = forms.ChoiceField(
        choices=DELIVERY_TIME,
        required=False
    )

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=PAYMENT_CHOICES
    )


class BillingAddressForm(forms.Form):

    billing_address_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=BILLING_ADDRESS_OPTION
    )
