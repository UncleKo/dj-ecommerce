from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from ..forms import CheckoutForm
from ..models import Order
from users.models import ShippingAddress
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect


class CheckoutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = CheckoutForm(self.request.user or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # Edit時はDBに保存されたデータをFormに結びつける
            # if order.shipping_address:
            #     form = CheckoutForm(self.request.user or None, {
            #                         'street_address': order.shipping_address.street_address,
            #                         'city': order.shipping_address.city,
            #                         'state': order.shipping_address.state,
            #                         'zip': order.shipping_address.zip,
            #                         'country': order.shipping_address.country
            #                         })

        except ObjectDoesNotExist:
            # messages.error(self.request, "You do not have an active order")
            return redirect("core:shopping-cart")

        context = {
            'form': form,
            'order': order,
            'primary_shipping_address': ShippingAddress.objects.filter(user=self.request.user, primary=True).first()
        }
        return render(self.request, "checkout/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.user or None,
                            self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            # print(self.request.POST)
            if form.is_valid():
                # print(form.cleaned_data)
                # print("The form is valid")
                shipping_address_option = form.cleaned_data.get(
                    'shipping_address_option')
                street_address = form.cleaned_data.get('street_address')
                city = form.cleaned_data.get('city')
                state = form.cleaned_data.get('state')
                zip = form.cleaned_data.get('zip')
                country = form.cleaned_data.get('country')
                delivery_time = form.cleaned_data.get('delivery_time')
                payment_option = form.cleaned_data.get('payment_option')
                # save_info = form.cleaned_data.get('save_info')

                # shipping_addresses = ShippingAddress.objects.filter(user=self.request.user)
                shipping_addresses = self.request.user.shipping_addresses.all()

                if shipping_address_option == 'A':
                    # order.shipping_address = ShippingAddress.objects.filter(
                    #     user=self.request.user, primary=True).first()
                    order.shipping_address = shipping_addresses.filter(
                        primary=True).first()

                elif shipping_address_option == 'B' or not shipping_addresses.count():
                    if street_address and city and state and zip:
                        shipping_address = ShippingAddress(
                            user=self.request.user,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip=zip,
                            country=country
                        )
                        shipping_address.save()

                        for stored_shipping_address in shipping_addresses:
                            stored_shipping_address.primary = False
                            stored_shipping_address.save()
                        shipping_address.primary = True
                        shipping_address.save()

                        order.shipping_address = shipping_address
                    else:
                        messages.warning(
                            self.request, "please fill in all fields in shipping address.")
                        return redirect('core:checkout')

                else:
                    messages.warning(
                        self.request, "please choose one of the radio box regarding shipping address.")
                    return redirect('core:checkout')

                order.delivery_time = delivery_time
                order.payment_option = payment_option
                # order.save_info
                order.save()

                if payment_option == 'C':
                    return redirect('core:billing-address')
                elif payment_option == 'B':
                    return redirect("core:order-summary")
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')

            messages.warning(self.request, "Something was wrong on the form")
            return redirect('core:checkout')

        except ObjectDoesNotExist:
            # messages.error(self.request, "You do not have an active order")
            return redirect("core:shopping-cart")
