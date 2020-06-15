from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import PAYMENT_CHOICES, DELIVERY_TIME, ShippingAddress, BillingAddress

BILLING_ADDRESS_OPTION = (
    ('A', 'Billing address is the same as my shipping address'),
    ('B', 'If it is already in the list below, please select it (to avoid duplication on your data).'),
)


class CheckoutForm(forms.Form):

    # first_name = forms.CharField(
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-control'
    #     }),
    #     # required=True
    # )
    # last_name = forms.CharField(
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-control'
    #     }),
    #     # required=True
    # )

    use_stored_shipping_address = forms.BooleanField(required=False)
    # fill_in_new_shipping_address = forms.BooleanField(required=False)
    stored_address = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        # queryset=ShippingAddress.objects.all(),
        queryset=None,
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
        widget=forms.RadioSelect,
        choices=PAYMENT_CHOICES
    )

    def __init__(self, user, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        self.fields['stored_address'].queryset = ShippingAddress.objects.filter(
            user=user)
        if not user.shipping_addresses.count():
            self.fields['street_address'].required = True
            self.fields['city'].required = True
            self.fields['state'].required = True
            self.fields['zip'].required = True

    # save_info = forms.BooleanField(required=False)

    # class Meta:
    #     model = Order
    #     fields = ['payment_option', 'delivery_time']


class BillingAddressForm(forms.Form):

    # same_billing_address = forms.BooleanField(required=False)
    # use_stored_billing_address = forms.BooleanField(required=False)
    billing_address_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=BILLING_ADDRESS_OPTION
    )

    stored_billing_address = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        queryset=BillingAddress.objects.all(),
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

    def __init__(self, user, *args, **kwargs):
        super(BillingAddressForm, self).__init__(*args, **kwargs)
        self.fields['stored_billing_address'].queryset = BillingAddress.objects.filter(
            user=user)
        if not user.billing_addresses.count():
            self.fields['street_address'].required = True
            self.fields['city'].required = True
            self.fields['state'].required = True
            self.fields['zip'].required = True

# class OrderForm(forms.Form):

#     delivery_time = forms.ChoiceField(
#         choices=DELIVERY_TIME,
#         required=False
#     )

#     payment_option = forms.ChoiceField(
#         widget=forms.RadioSelect, choices=PAYMENT_CHOICES
#     )

#     same_billing_address = forms.BooleanField(required=False)

#     # save_info = forms.BooleanField(required=False)

#     class Meta:
#         model = Order
#         fields = ['payment_option', 'delivery_time']


# CheckoutForm = inlineformset_factory(
#     ShippingAddress,
#     Order,
#     form=OrderForm,
#     fields=['delivery_time', 'payment_option'],
#     extra=1,
#     # can_delete=True
# )
