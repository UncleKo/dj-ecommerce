from django import forms
from django.forms.models import inlineformset_factory
from .models import Item, PAYMENT_CHOICES, DELIVERY_TIME, Inquiry, SizeOption, ColorOption
from users.models import ShippingAddress, BillingAddress
from photos.models import Photo


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
        widget=forms.RadioSelect,
        choices=BILLING_ADDRESS_OPTION
    )


class ContactForm(forms.ModelForm):

    class Meta:
        model = Inquiry
        fields = ['subject', 'name', 'email', 'content']


class ItemOptionForm(forms.Form):

    size_option = forms.ModelChoiceField(
        widget=forms.Select(attrs={
            'class': 'select form-control'
        }),
        # choices="",
        queryset=None,
        label="サイズ",
        required=False
    )

    color_option = forms.ModelChoiceField(
        widget=forms.Select(attrs={
            'class': 'select form-control'
        }),
        # choices="",
        queryset=None,
        label="カラー",
        required=False
    )

    quantity = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'select form-control'
        }),
        choices=(('1', '1'), ('2', '2'), ('3', '3'),
                 ('4', '4'), ('5', '5'), ('6', '6')),
        label="数量",
        required=False
    )

    def __init__(self, item, *args, **kwargs):
        super(ItemOptionForm, self).__init__(*args, **kwargs)
        if item.size_option.count():
            # self.fields['size_option'].choices = item.size_option.all().order_by(
            #     'id').values_list('value', 'value')
            self.fields['size_option'].queryset = SizeOption.objects.filter(
                item=item).order_by('id')
            self.fields['size_option'].required = True
        if item.color_option.count():
            self.fields['color_option'].queryset = ColorOption.objects.filter(
                item=item).order_by('id')
            self.fields['color_option'].required = True
        # if item.stock:
        #     self.fields['quantity'].choices = item.stock


# class ItemOptionInFavItemsForm(forms.Form):

#     size_option = forms.ModelChoiceField(
#         widget=forms.Select(attrs={
#             'class': 'select form-control'
#         }),
#         queryset=SizeOption.objects.filter(item=item).order_by('id'),
#         label="サイズ",
#         required=False
#     )

#     color_option = forms.ModelChoiceField(
#         widget=forms.Select(attrs={
#             'class': 'select form-control'
#         }),
#         queryset=SizeOption.objects.filter(item=item).order_by('id'),
#         label="カラー",
#         required=False
#     )


class ItemCreateForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['title', 'price', 'discount_price', 'category',
                  'description', 'stock', 'draft', 'pickup', 'featured', 'image']


PhotoFormset = inlineformset_factory(
    Item,
    Photo,
    # fields=['origin', 'order', 'category', 'tags', 'private'],
    fields=['origin', 'order'],
    extra=10,
    max_num=10,
    # can_delete=False,
    # attrs={
    #     'class': 'select form-control'
    # }
)


class EditMultipleItemsForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'readonly': 'readonly'
        })
    )

    # price = forms.IntegerField(
    #     widget=forms.TextInput(attrs={
    #         'readonly': 'readonly'
    #     })
    # )


EditMultipleItemsFormSet = forms.modelformset_factory(
    Item,
    form=EditMultipleItemsForm,
    fields=['title', 'draft', 'pickup', 'featured'],
    extra=0,
    max_num=10
)
