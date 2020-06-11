from .models import Item, OrderItem, Order, ShippingAddress, BillingAddress, Payment
from .forms import CheckoutForm
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
# from django.db.models import F

# Email
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class HomeView(ListView):
    model = Item
    template_name = "home.html"
    context_object_name = 'items'
    paginate_by = 10

# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "home.html", context)


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"
    context_object_name = 'item'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return render(self.request, 'order_summary.html')

# def order_summary_view(request):
#     try:
#         order = Order.objects.get(user=request.user, ordered=False)
#         context = {
#             'object': order
#         }
#         return render(request, 'order_summary.html', context)
#     except Order.DoesNotExist:
#         messages.error(request, "You do not have an active order")
#         return redirect("/")


class CheckoutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        # order = Order.objects.get(user=self.request.user, ordered=False)
        order = get_object_or_404(Order, user=self.request.user, ordered=False)

        context = {
            'form': form,
            'order': order,
            # 'shipping_addresses': ShippingAddress.objects.filter(user=self.request.user)
            'shipping_address': ShippingAddress.objects.filter(user=self.request.user).get(pk=1)
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        # order = get_object_or_404(user=self.request.user, ordered=False)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            # print(self.request.POST)
            if form.is_valid():
                # print(form.cleaned_data)
                # print("The form is valid")
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields
                use_stored_shipping_address = form.cleaned_data.get(
                    'use_stored_shipping_address')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                delivery_time = form.cleaned_data.get('delivery_time')

                if use_stored_shipping_address:
                    shipping_address = ShippingAddress.objects.filter(
                        user=self.request.user).get(pk=1)
                    order.shipping_address = shipping_address
                    if same_billing_address:
                        billing_address = BillingAddress(
                            user=self.request.user,
                            street_address=shipping_address.street_address,
                            apartment_address=shipping_address.apartment_address,
                            country=shipping_address.country,
                            zip=shipping_address.zip
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                else:
                    shipping_address = ShippingAddress(
                        user=self.request.user,
                        street_address=street_address,
                        apartment_address=apartment_address,
                        country=country,
                        zip=zip
                    )
                    shipping_address.save()
                    order.shipping_address = shipping_address
                    if same_billing_address:
                        billing_address = BillingAddress(
                            user=self.request.user,
                            street_address=street_address,
                            apartment_address=apartment_address,
                            country=country,
                            zip=zip
                        )
                        billing_address.save()
                        order.billing_address = billing_address

                order.delivery_time = delivery_time
                order.payment_option = payment_option
                order.save()

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'B':
                    order_items = order.items.all()
                    order_items.update(ordered=True)
                    for item in order_items:
                        item.save()

                    order.ordered = True
                    order.save()

                    msg_plain = render_to_string('email.txt', {
                        'order': order
                    })
                    # msg_html = render_to_string('templates/email.html', {
                    #     'some_params': some_params
                    # })

                    send_mail(
                        f'{self.request.user.username}, Thank you for the shopping!',
                        # f'{order.id} at {order.ordered_date}',
                        msg_plain,
                        'uncleko496@gmail.com',
                        ['uncleko496@gmail.com', self.request.user.email],
                        # html_message=msg_html,
                        # fail_silently=False,
                    )

                    messages.success(
                        self.request, "Your order was successful!")
                    return redirect("/")

                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')

            messages.warning(self.request, "Failed checkout")
            return redirect('core:checkout')

        except ObjectDoesNotExist:
            message.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        # if self.kwargs.get('payment_option') == 'stripe':
        order = Order.objects.get(user=self.request.user, ordered=False)
        # if order.billing_address:
        context = {
            'order': order,
            # 'DISPLAY_COUPON_FORM': False
        }
        return render(self.request, "payment.html", context)
        # else:
        #     messages.warning(
        #         self.request, "You have not added a billing address")
        #     return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            # # To avoid a race condition:  2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished.
            # order_item.quantity = F('quantity') + 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
    else:
        messages.info(request, "You do not have an active order.")
    return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
    else:
        messages.info(request, "You do not have an active order.")
    return redirect("core:product", slug=slug)
