from django.urls import reverse_lazy
# from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from core.boost import DynamicRedirectMixin
# from django.urls import reverse_lazy

from django.contrib.sites.models import Site
from ..models import Item, Order, SiteInfo, Category, Inquiry
from ..forms import CheckoutForm, BillingAddressForm, InquiryForm
from users.models import ShippingAddress, BillingAddress
# from .boost import DynamicRedirectMixin

# Email
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context


class InquiryCreateView(CreateView):
    model = Inquiry
    form_class = InquiryForm

    def post(self, *args, **kwargs):
        form = InquiryForm(self.request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            name = form.cleaned_data.get('name')
            content = form.cleaned_data.get('content')
            form.save()
            msg_plain = render_to_string('parts/email-inquiry.txt', {
                'content': content,
                'name': name,
                'subject': subject
            })
            # msg_html = render_to_string('parts/inquiry-email.html', {
            #     'inquiry': form
            # })
            send_mail(
                f'お問い合わせありがとうございます。',
                msg_plain,
                'uncleko496@gmail.com',
                ['uncleko496@gmail.com', email],
                # html_message=msg_html,
                # fail_silentl,
            )
            messages.success(self.request, "お問い合わせありがとうございます。")
            return redirect(self.request.META['HTTP_REFERER'])


class SiteInfoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SiteInfo
    fields = ['title', 'free_shippment_line', 'shipping_fee',
              'order_history_paginate_by', 'order_list_paginate_by']
    # success_url = reverse_lazy('core:siteinfo')
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        form.instance.site_id = 1
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class HomeView(ListView):
    model = Item
    template_name = "core/home.html"
    context_object_name = 'items'
    # ordering = ['?']

    def get_queryset(self):
        return Item.objects.filter(draft=False).order_by('?')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_item"] = Item.objects.filter(featured=True).first()
        context["categories"] = Category.objects.all().order_by('order')

        return context

# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "core/home.html", context)


class CategoryItemListView(ListView):
    model = Item
#   template_name = 'core/item_list.html'
    context_object_name = 'items'
    paginate_by = 5

    def get_queryset(self):
        category = get_object_or_404(
            Category, name=self.kwargs.get('category_name'))
        return category.items.filter(draft=False).order_by('?')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by('order')

        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = "core/item.html"
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["other_items"] = Item.objects.exclude(
            slug=self.kwargs['slug']).order_by('?')[:3]
        context["categories"] = Category.objects.all().order_by('order')
        # if self.get_object().fav_users.filter(id=self.request.user.id):
        if self.object.fav_users.filter(id=self.request.user.id):
            context["already_favorite"] = True
        return context


class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, ListView):
    model = Category
    success_url = reverse_lazy('core:category-list')
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all().order_by('order')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, CreateView):
    model = Category
    fields = ['name', 'order']
    success_url = reverse_lazy('core:category-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context_processors.pyでサイトすべてに渡す手も
        context["categories"] = Category.objects.all()
        return context

    # ユーザーがスタッフの時にのみ許可
    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, UpdateView):
    model = Category
    fields = ['name', 'order']
    success_url = reverse_lazy('core:category-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context_processors.pyでサイトすべてに渡す手も
        context["categories"] = Category.objects.all()
        context["edit"] = 1
        return context

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, DeleteView):
    model = Category
    context_object_name = 'category'
    success_url = reverse_lazy('core:category-list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = self.object.items.all()
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


class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'core/shopping-cart.html', context)
        except ObjectDoesNotExist:
            # messages.error(self.request, "ショッピングカートに商品はありません")
            return render(self.request, 'core/shopping-cart.html')


class CheckoutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            return redirect("core:shopping-cart")

        context = {
            'form': form,
            'order': order,
            'primary_shipping_address': ShippingAddress.objects.filter(user=self.request.user, primary=True).first()
        }
        return render(self.request, "checkout/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                delivery_time = form.cleaned_data.get('delivery_time')
                payment_option = form.cleaned_data.get('payment_option')

                shipping_addresses = self.request.user.shipping_addresses.all()

                order.shipping_address = shipping_addresses.filter(
                    primary=True).first()

                order.delivery_time = delivery_time
                order.payment_option = payment_option

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


class BillingAddressView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = BillingAddressForm()
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
            'first_billing_address': BillingAddress.objects.filter(user=self.request.user).first(),
            'primary_billing_address': BillingAddress.objects.filter(user=self.request.user, primary=True).first()
        }
        return render(self.request, "checkout/billing-address.html", context)

    def post(self, *args, **kwargs):
        form = BillingAddressForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                billing_address_option = form.cleaned_data.get(
                    'billing_address_option')

                if billing_address_option == 'A':

                    billing_addresses = self.request.user.billing_addresses.all()
                    order.billing_address = billing_addresses.filter(
                        primary=True).first()

                elif billing_address_option == 'B':
                    already_stored_billing_address = BillingAddress.objects.filter(
                        street_address=order.shipping_address.street_address,
                        city=order.shipping_address.city,
                        state=order.shipping_address.state,
                        zip=order.shipping_address.zip
                    )
                    if already_stored_billing_address:
                        billing_address = already_stored_billing_address
                    else:
                        billing_address = BillingAddress(
                            user=self.request.user,
                            street_address=order.shipping_address.street_address,
                            city=order.shipping_address.city,
                            state=order.shipping_address.state,
                            zip=order.shipping_address.zip,
                        )

                        billing_addresses = self.request.user.billing_addresses.all()
                        for stored_billing_address in billing_addresses:
                            stored_billing_address.primary = False
                            stored_billing_address.save()
                        billing_address.primary = True

                        billing_address.save()
                        order.billing_address = billing_address

                else:
                    messages.warning(
                        self.request, "ラジオボックスをひとつご選択ください。")
                    return redirect('core:billing-address')

                order.save()
                return redirect("core:order-summary")

            messages.warning(
                self.request, "ラジオボックスをひとつご選択ください。")
            return redirect('core:billing-address')

        except objectdoesnotexist:
            return redirect("core:shopping-cart")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            if not order.shipping_address or not order.payment_option:
                messages.warning(
                    self.request, "必要な情報をすべて入力し直してください。")
                # Where should they go back? shopping cart? checkout?
                # return render(self.request, 'checkout/order-summary.html', context)
            return render(self.request, 'checkout/order-summary.html', context)
            # else:
            #     messages.error(
            #         self.request, "Please Provide All Information We need.")
            #     return render(self.request, 'checkout/order-summary.html')

        except ObjectDoesNotExist:
            messages.error(self.request, "カートに何も入ってません。")
            return render(self.request, 'checkout/order-summary.html')


class OrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    model = Order
    template_name = 'core/order-list.html'
    context_object_name = 'orders'
    paginate_by = Site.objects.get_current().siteinfo.order_list_paginate_by

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


def email_test(request):
    order = Order.objects.get(pk=3)
    context = {
        'order': order
    }
    return render(request, 'parts/email.html', context)
