from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from ..forms import BillingAddressForm
from ..models import Order
from users.models import BillingAddress
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404


class BillingAddressView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = BillingAddressForm(self.request.user or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if not order.shipping_address:
                messages.error(
                    self.request, "Please provide your shipping address first.")
                return redirect("core:checkout")

        except ObjectDoesNotExist:
            return redirect("core:shopping-cart")

        context = {
            'form': form,
            'order': order,
            'first_billing_address': BillingAddress.objects.filter(user=self.request.user).first()
        }
        return render(self.request, "checkout/billing-address.html", context)

    def post(self, *args, **kwargs):
        form = BillingAddressForm(
            self.request.user or None, self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                billing_address_option = form.cleaned_data.get(
                    'billing_address_option')
                stored_billing_address = form.cleaned_data.get(
                    'stored_billing_address')
                street_address = form.cleaned_data.get('street_address')
                city = form.cleaned_data.get('city')
                state = form.cleaned_data.get('state')
                zip = form.cleaned_data.get('zip')
                country = form.cleaned_data.get('country')
                # same_billing_address = form.cleaned_data.get('same_billing_address')

                if billing_address_option == 'A':
                    # 保存データに既にある場合、そっちを持ってくる（新しく作らない）
                    # already_stored_billing_address = get_object_or_404(
                    #     BillingAddress, street_address=order.shipping_address.street_address)
                    # if already_stored_billing_address:
                    #     billing_address = already_stored_billing_address
                    # else:
                    billing_address = BillingAddress(
                        user=self.request.user,
                        street_address=order.shipping_address.street_address,
                        city=order.shipping_address.city,
                        state=order.shipping_address.state,
                        zip=order.shipping_address.zip,
                        country=order.shipping_address.country
                    )
                    billing_address.save()
                    order.billing_address = billing_address

                elif billing_address_option == 'B':

                    if self.request.user.billing_addresses.count() == 1:
                        order.billing_address = self.request.user.billing_addresses.first()
                    elif stored_billing_address:
                        billing_address = BillingAddress.objects.filter(
                            user=self.request.user).get(pk=stored_billing_address.id)
                        order.billing_address = billing_address
                    else:
                        messages.warning(
                            self.request, "please check the radio box of the address you pick up.")
                        return redirect('core:billing-address')

                elif billing_address_option == 'C':
                    if street_address and city and state and zip:
                        billing_address = BillingAddress(
                            user=self.request.user,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip=zip,
                            country=country
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                    else:
                        messages.warning(
                            self.request, "please fill in all fields in billing address.")
                        return redirect('core:billing-address')
                else:
                    # Error (returned None instead)
                    messages.warning(
                        self.request, "please choose one of the radio box regarding billing address.")
                    return redirect('core:billing-address')

                order.save()
                return redirect("core:order-summary")

            messages.warning(
                self.request, "please choose one of the radio box regarding billing address.")
            return redirect('core:billing-address')

        except objectdoesnotexist:
            return redirect("core:shopping-cart")
