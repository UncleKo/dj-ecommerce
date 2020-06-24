from django.conf import settings
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.models import User
from ..models import Order
from django.shortcuts import render, redirect

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentView(View):
    def get(self, *args, **kwargs):
        # if self.kwargs.get('payment_option') == 'stripe':
        order = Order.objects.get(user=self.request.user, ordered=False)
        # if order.billing_address:
        context = {
            'order': order,
            # 'DISPLAY_COUPON_FORM': False
        }
        return render(self.request, "checkout/payment.html", context)
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
            for order_item in order_items:
                if order_item.item.stock:
                    order_item.item.stock -= order_item.quantity
                    order_item.item.save()
                order_item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            # order_items.delete()

            msg_plain = render_to_string('parts/email.txt', {
                'order': order
            })
            msg_html = render_to_string('parts/email.html', {
                'some_params': some_params
            })

            send_mail(
                f'{self.request.user.username}, Thank you for the shopping!',
                # f'{order.id} at {order.ordered_date}',
                msg_plain,
                'uncleko496@gmail.com',
                ['uncleko496@gmail.com', self.request.user.email],
                html_message=msg_html,
                # fail_silently=False,
            )

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
