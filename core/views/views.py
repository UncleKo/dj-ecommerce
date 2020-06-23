from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib.auth.models import User
# from django.db.models import F
# from django.urls import reverse_lazy

from ..models import Item, OrderItem, Order, Payment
from users.models import ShippingAddress, BillingAddress
from ..forms import PrimaryShippingAddressForm
# from .boost import DynamicRedirectMixin

# Email
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context


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


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'shopping-cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return render(self.request, 'shopping-cart.html')


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            if not order.shipping_address or not order.payment_option:
                messages.warning(
                    self.request, "Please Provide All Information We need.")
                # Where should they go back? shopping cart? checkout?
                # return render(self.request, 'checkout/order-summary.html', context)
            return render(self.request, 'checkout/order-summary.html', context)
            # else:
            #     messages.error(
            #         self.request, "Please Provide All Information We need.")
            #     return render(self.request, 'checkout/order-summary.html')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return render(self.request, 'checkout/order-summary.html')


@login_required
def confirm_order(request):

    try:
        order = Order.objects.get(user=request.user, ordered=False)

        if not request.user.first_name or not request.user.last_name or not order.get_total or not order.shipping_address or not order.payment_option:
            messages.warning(
                request, "Please Provide All Information We need.")
            # Where should they go back? shopping cart? checkout?
            return redirect('core:order-summary')

        if order.payment_option == 'C':
            return redirect('core:payment', payment_option='stripe')

        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
        order.ordered = True
        order.save()
        # for item in order_items:
        #   ,
        msg_plain = render_to_string('parts/email.txt', {
            'order': order
        })
        msg_html = render_to_string('parts/email.html', {
            'order': order
        })
        send_mail(
            f'{request.user.first_name}, Thank you for the shopping!',
            # f'{order.id} at {order.ordered_date}',
            msg_plain,
            'uncleko496@gmail.com',
            ['uncleko496@gmail.com', request.user.email],
            html_message=msg_html,
            # fail_silentl,
        )
        messages.success(request, "Thank you so much for the shopping!")
        return render(request, 'shopping-cart.html')

    except ObjectDoesNotExist:
        messages.error(request, "You do not have an active order")
        return render(request, 'shopping-cart.html')


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
    return redirect("core:shopping-cart")


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
            return redirect("core:shopping-cart")
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
            return redirect("core:shopping-cart")
        else:
            messages.info(request, "This item was not in your cart.")
    else:
        messages.info(request, "You do not have an active order.")
    return redirect("core:product", slug=slug)


class PrimaryShippingAddress(LoginRequiredMixin, View):

    # # DynamicRedirectMixinが効かない原因
    # success_url = reverse_lazy('core:primary-shipping-address')

    def get(self, *args, **kwargs):
        form = PrimaryShippingAddressForm(self.request.user or None)
        context = {
            'form': form
        }
        return render(self.request, "checkout/primary-shipping-address.html", context)

    def post(self, *args, **kwargs):
        form = PrimaryShippingAddressForm(self.request.user or None,
                                          self.request.POST or None)
        try:
            shipping_addresses = ShippingAddress.objects.filter(
                user=self.request.user)
            if form.is_valid():
                list_stored_address = form.cleaned_data.get(
                    'list_stored_address')

            # for address in stored_adress:
            #     address.primary = False

            if list_stored_address:
                for shipping_address in shipping_addresses:
                    shipping_address.primary = False
                    shipping_address.save()
                primary_shipping_address = shipping_addresses.get(
                    pk=list_stored_address.id)
                primary_shipping_address.primary = True
                primary_shipping_address.save()
                return redirect("core:checkout")
            else:
                messages.warning(
                    self.request, "Please choose one of the stored address as shipping address.")
                return redirect("core:primary-shipping-address")

        except ObjectDoesNotExist:
            messages.error(
                self.request, "You do not have stored shipping addresses")
            return redirect("core:checkout")
