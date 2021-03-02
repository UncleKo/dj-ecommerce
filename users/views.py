from django.contrib import messages
from django.shortcuts import render, redirect, resolve_url  # get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import is_safe_url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from core.boost import DynamicRedirectMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from .models import ShippingAddress, BillingAddress
from core.models import Order, Item, Category, SiteInfo
from .forms import UserUpdateForm, ProfileUpdateForm, ShippingAddressForm, PrimaryShippingAddressForm, UserRegisterForm, BillingAddressForm, PrimaryBillingAddressForm
from core.forms import ItemOptionForm


class ProfileView(LoginRequiredMixin, DynamicRedirectMixin, View):
    # model = User
    # template_name = 'users/profile.html'
    def get(self, *args, **kwargs):
        return render(self.request, "users/profile.html")

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["orders"] = Order.objects.filter(
    #         user=self.request.user,
    #         ordered=True
    #     )
    #     return context

    # def test_func(self):
    #     user = self.get_object()
    #     if self.request.user == user:
    #         return True
    #     return False


# class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = User
#     form_class = ProfileUpdateForm
#     template_name = 'users/profile-edit.html'
#     success_url = reverse_lazy('user:profile')

#     # def get_success_url(self):
#     # return reverse("user:profile", kwargs={
#     #     'pk': self.kwargs['pk']
#     # })
#     # return resolve_url('user:profile', pk=self.kwargs['pk'])

#     def test_func(self):
#         user = self.get_object()
#         if self.request.user == user:
#             return True
#         return False


class FavItemsListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = "users/fav_items.html"
    context_object_name = 'fav_items'
    # paginate_by = 3
    ordering = ['-id']
    # ordering = ['?']

    def get_queryset(self):
        return Item.objects.filter(fav_users=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        for item in self.object_list:
            context["form"] = ItemOptionForm(item)

        return context

    # def test_func(self):
    #     user = self.get_object().fav_user
    #     if self.request.user == user:
    #         return True
    #     return False


class OrderHistoryView(LoginRequiredMixin, ListView):

    model = Order
    template_name = 'core/order-list.html'
    context_object_name = 'orders'
    paginate_by = Site.objects.get_current().siteinfo.order_history_paginate_by

    def get_queryset(self):
        # user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Order.objects.filter(user=self.request.user, ordered=True).order_by('-ordered_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history"] = 1

        return context

    # def test_func(self):
    #     user = get_object_or_404(User, pk=self.kwargs.get('pk'))
    #     if self.request.user == user:
    #         return True
    #     return False


class ShippingAddressCreateView(LoginRequiredMixin, DynamicRedirectMixin, CreateView):
    model = ShippingAddress
    form_class = ShippingAddressForm
    # template_name = 'users/shipping_address_form.html'
    success_url = reverse_lazy('user:profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        shipping_addresses = self.request.user.shipping_addresses.all()
        for shipping_address in shipping_addresses:
            shipping_address.primary = False
            shipping_address.save()
        form.instance.primary = True

        return super().form_valid(form)


class ShippingAddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, UpdateView):
    model = ShippingAddress
    form_class = ShippingAddressForm
    success_url = reverse_lazy('user:profile')

    def test_func(self):
        user = self.get_object().user
        if self.request.user == user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edit"] = 1
        return context


class ShippingAddressDeleteView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, DeleteView):
    model = ShippingAddress
    success_url = reverse_lazy('user:profile')

    def test_func(self):
        user = self.get_object().user
        # primary = self.get_object().primary
        # if self.request.user == user and not primary:
        if self.request.user == user:
            # # Just for insurance
            # if self.get_object().primary:
            #     messages.warning(
            #         self.request, "削除するには優先住所から外して下さい(他の住所を優先住所に指定して下さい)。")
            #     # it didn't work. I don't know why.
            #     return redirect("user:primary-shipping-address")
            # else:
            return True
        return False


class PrimaryShippingAddress(LoginRequiredMixin, SuccessURLAllowedHostsMixin, View):

    # # DynamicRedirectMixinが効かない原因
    # success_url = reverse_lazy('core:primary-shipping-address')

    def get(self, *args, **kwargs):
        form = PrimaryShippingAddressForm(self.request.user or None)
        primary_address = ShippingAddress.objects.filter(
            user=self.request.user, primary=True).first()
        if(primary_address):
            primary_id = primary_address.id
        else:
            primary_id = None
        context = {
            'form': form,
            'primary_id': primary_id
            # 'shipping_addresses': ShippingAddress.objects.filter(user=self.request.user)
        }
        return render(self.request, "users/primary-shipping-address.html", context)

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
                # return redirect("core:checkout")

                redirect_field_name = 'next'
                redirect_to = self.request.POST.get(
                    self.redirect_field_name,
                    self.request.GET.get(self.redirect_field_name, '')
                )
                url_is_safe = is_safe_url(
                    url=redirect_to,
                    allowed_hosts=self.get_success_url_allowed_hosts(),
                    require_https=self.request.is_secure(),
                )
                return redirect(redirect_to) if url_is_safe else ''
                # redirect_to_next(self)

            else:
                messages.warning(
                    self.request, "優先住所をひとつ選択ください。")
                return redirect("user:primary-shipping-address")

        except ObjectDoesNotExist:
            messages.error(
                self.request, "配送先住所の登録がありません。")
            return redirect("core:checkout")


class BillingAddressCreateView(LoginRequiredMixin, DynamicRedirectMixin, CreateView):
    model = BillingAddress
    form_class = BillingAddressForm
    success_url = reverse_lazy('user:profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        billing_addresses = self.request.user.billing_addresses.all()
        for billing_address in billing_addresses:
            billing_address.primary = False
            billing_address.save()
        form.instance.primary = True

        return super().form_valid(form)


class BillingAddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, UpdateView):
    model = BillingAddress
    form_class = BillingAddressForm
    success_url = reverse_lazy('user:profile')

    def test_func(self):
        user = self.get_object().user
        if self.request.user == user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edit"] = 1
        return context


class BillingAddressDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BillingAddress
    success_url = reverse_lazy('user:profile')

    def test_func(self):
        user = self.get_object().user
        if self.request.user == user:
            return True
        return False


class PrimaryBillingAddress(LoginRequiredMixin, SuccessURLAllowedHostsMixin, View):

    def get(self, *args, **kwargs):
        form = PrimaryBillingAddressForm(self.request.user or None)
        primary_address = BillingAddress.objects.filter(
            user=self.request.user, primary=True).first()
        if(primary_address):
            primary_id = primary_address.id
        else:
            primary_id = None
        context = {
            'form': form,
            'primary_id': primary_id
        }
        return render(self.request, "users/primary-billing-address.html", context)

    def post(self, *args, **kwargs):
        form = PrimaryBillingAddressForm(self.request.user or None,
                                         self.request.POST or None)
        try:
            billing_addresses = BillingAddress.objects.filter(
                user=self.request.user)
            if form.is_valid():
                list_stored_address = form.cleaned_data.get(
                    'list_stored_address')

            # for address in stored_adress:
            #     address.primary = False

            if list_stored_address:
                for billing_address in billing_addresses:
                    billing_address.primary = False
                    billing_address.save()
                primary_billing_address = billing_addresses.get(
                    pk=list_stored_address.id)
                primary_billing_address.primary = True
                primary_billing_address.save()
                # return redirect("core:checkout")

                redirect_field_name = 'next'
                redirect_to = self.request.POST.get(
                    self.redirect_field_name,
                    self.request.GET.get(self.redirect_field_name, '')
                )
                url_is_safe = is_safe_url(
                    url=redirect_to,
                    allowed_hosts=self.get_success_url_allowed_hosts(),
                    require_https=self.request.is_secure(),
                )
                return redirect(redirect_to) if url_is_safe else ''
                # redirect_to_next(self)

            else:
                messages.warning(
                    self.request, "優先住所をひとつ選択ください")
                return redirect("user:primary-billing-address")

        except ObjectDoesNotExist:
            messages.error(
                self.request, "請求先住所が登録されてません。")
            return redirect("user:primary-billing-address")


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            # to avoid re-post request to the page( if reached to reander it will re-post)
            return redirect('user:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile-edit.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.info(
                request, "Thanks for registering. You are now logged in.")
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            send_mail(
                'ご登録ありがとうございます',
                f'ユーザー名:{request.user.username}として会員登録が完了致しました。',
                'uncleko496@gmail.com',
                [request.user.email, 'uncleko496@gmail.com'],
                fail_silently=False,
            )
            return redirect('user:profile')  # or blog-home, etc..
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
