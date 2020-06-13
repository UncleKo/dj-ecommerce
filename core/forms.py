from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import PAYMENT_CHOICES, DELIVERY_TIME, ShippingAddress, BillingAddress

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

BILLING_ADDRESS = (
    ('A', 'Billing address is the same as my shipping address'),
    ('B', 'Use the address below as my billing address(if some exits).')
)


class CheckoutForm(forms.Form):
    use_stored_shipping_address = forms.BooleanField(required=False)
    stored_address = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        queryset=ShippingAddress.objects.all(),
        required=False,
        empty_label=None
    )
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '1234 Main St #101',
            'class': 'form-control'
        }),
        required=False
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Los Angeles',
            'class': 'form-control'
        }),
        required=False
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'CA',
            'class': 'form-control'
        }),
        required=False
    )

    zip = forms.CharField(
        widget=forms.TextInput(attrs={
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

    delivery_time = forms.ChoiceField(
        choices=DELIVERY_TIME,
        required=False
    )

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES
    )

    # same_billing_address = forms.BooleanField(required=False)
    # use_stored_billing_address = forms.BooleanField(required=False)
    billing_address = forms.ChoiceField(
        widget=forms.RadioSelect, choices=BILLING_ADDRESS
    )

    stored_billing_address = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        queryset=BillingAddress.objects.all(),
        required=False,
        empty_label=None
    )

    # save_info = forms.BooleanField(required=False)

    # class Meta:
    #     model = Order
    #     fields = ['payment_option', 'delivery_time']
