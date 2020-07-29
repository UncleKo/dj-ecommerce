from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.utils import timezone
from django.contrib.auth.models import User
# from django.db.models import F
# from django.urls import reverse_lazy

from ..models import Item, OrderItem, Order, Payment
from ..models import CATEGORY_CHOICES
from users.models import ShippingAddress, BillingAddress
# from .boost import DynamicRedirectMixin

# Email
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context


class HomeView(ListView):
    model = Item
    template_name = "core/home.html"
    context_object_name = 'items'
    # paginate_by = 3
    # ordering = ['-id']
    ordering = ['?']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_item"] = Item.objects.filter(featured=True).first()
        context["category_choices"] = CATEGORY_CHOICES

        return context

# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "core/home.html", context)


class ItemDetailView(DetailView):
    model = Item
    template_name = "core/item.html"
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["other_items"] = Item.objects.exclude(
            slug=self.kwargs['slug']).order_by('?')[:3]
        context["category_choices"] = CATEGORY_CHOICES
        return context


class ItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Item
    fields = ['title', 'price', 'discount_price', 'category',
              'description', 'stock', 'featured', 'image', 'draft']

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ['title', 'price', 'discount_price', 'category',
              'description', 'stock', 'featured', 'image', 'draft', 'slug']

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edit"] = 1
        return context


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'core/shopping-cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return render(self.request, 'core/shopping-cart.html')


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


class OrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    model = Order
    template_name = 'core/order-list.html'
    context_object_name = 'orders'
    paginate_by = 2

    def get_queryset(self):
        return Order.objects.filter(ordered=True).order_by('-ordered_date')

    # ユーザーがスタッフの時にのみ許可
    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_for_staff"] = 1
        return context


class UserOrderListView(LoginRequiredMixin, ListView):

    model = Order
    template_name = 'core/order-list.html'
    context_object_name = 'orders'
    paginate_by = 2

    def get_queryset(self):
        # user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Order.objects.filter(user=self.request.user, ordered=True).order_by('-ordered_date')

    # def test_func(self):
    #     user = get_object_or_404(User, pk=self.kwargs.get('pk'))
    #     if self.request.user == user:
    #         return True
    #     return False


@permission_required('is_staff')
def order_dispatched(request, pk):
    order = get_object_or_404(Order, pk=pk)
    msg_plain = render_to_string('parts/email.txt', {
        'order': order,
        'dispatched': True
    })
    msg_html = render_to_string('parts/email.html', {
        'order': order,
        'dispatched': True
    })
    if order.dispatched:
        order.dispatched = False
    else:
        order.dispatched = True
        send_mail(
            f'Order no. {order.id} has been dispatched!',
            msg_plain,
            'uncleko496@gmail.com',
            [request.user.email, 'uncleko496@gmail.com'],
            html_message=msg_html,
            fail_silently=False,
        )
    order.save()
    # redirect to the same page (including paging)
    return redirect(request.META['HTTP_REFERER'])


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
        for order_item in order_items:
            if order_item.item.stock:
                order_item.item.stock -= order_item.quantity
                order_item.item.save()
            order_item.save()
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
        return render(request, 'core/shopping-cart.html')

    except ObjectDoesNotExist:
        messages.error(request, "You do not have an active order")
        return render(request, 'core/shopping-cart.html')


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
            if order_item.item.stock:
                if order_item.quantity < order_item.item.stock:
                    order_item.quantity += 1
                    # # To avoid a race condition:  2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished.
                    # order_item.quantity = F('quantity') + 1
                    order_item.save()
                    messages.info(request, "This item quantity was updated.")
                else:
                    messages.warning(
                        request, "You are tying to add the item over stock.")
            else:
                order_item.quantity += 1
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
    return redirect("core:item", slug=slug)


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
    return redirect("core:item", slug=slug)
