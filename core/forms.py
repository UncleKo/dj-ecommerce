from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import PAYMENT_CHOICES, DELIVERY_TIME  # , Order

# PAYMENT_CHOICES = (
#     ('S', 'Stripe'),
#     # ('P', 'PayPal'),
#     ('B', 'Bank Transfer')
# )

# DELIVERY_TIME = (
#     ('N', 'No Designation'),
#     ('A', 'morning'),
#     ('B', '0pm-2pm'),
#     ('C', '2pm-4pm'),
#     ('D', '4pm-6pm'),
#     ('E', '6pm-8pm')
# )


class CheckoutForm(forms.Form):
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '1234 Main St',
            'class': 'form-control'
        }),
        required=False
    )
    apartment_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Apartment or suite',
            'class': 'form-control'
        }),
        required=False
    )

    country = CountryField(
        blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }),
        required=False
    )
    zip = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        required=False
    )
    use_stored_shipping_address = forms.BooleanField(required=False)
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES
    )
    delivery_time = forms.ChoiceField(
        choices=DELIVERY_TIME
    )

    # class Meta:
    #     model = Order
    #     fields = ['payment_option', 'delivery_time']
