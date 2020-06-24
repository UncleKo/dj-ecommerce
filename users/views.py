from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.boost import DynamicRedirectMixin
from .models import ShippingAddress
from .forms import ProfileUpdateForm, AddressForm, PrimaryShippingAddressForm


class ProfileView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    # def get(self, *args, **kwargs):

    def test_func(self):
        user = self.get_object()
        if self.request.user == user:
            return True
        return False


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'users/edit-profile.html'
    success_url = reverse_lazy('profile')

    def test_func(self):
        user = self.get_object()
        if self.request.user == user:
            return True
        return False


class ShippingAddressCreateView(LoginRequiredMixin, DynamicRedirectMixin, CreateView):
    model = ShippingAddress
    form_class = AddressForm
    # template_name = 'users/shipping_address_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.primary = True
        return super().form_valid(form)


class ShippingAddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, UpdateView):
    model = ShippingAddress
    form_class = AddressForm
    success_url = reverse_lazy('profile')

    def test_func(self):
        user = self.get_object().user
        if self.request.user == user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edit"] = 1
        return context


class ShippingAddressDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ShippingAddress
    success_url = reverse_lazy('profile')

    def test_func(self):
        user = self.get_object().user
        # primary = self.get_object().primary
        # if self.request.user == user and not primary:
        if self.request.user == user:
            return True
        return False


class PrimaryShippingAddress(LoginRequiredMixin, View):

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
                return redirect("core:checkout")
            else:
                messages.warning(
                    self.request, "Please choose one of the stored address as shipping address.")
                return redirect("core:primary-shipping-address")

        except ObjectDoesNotExist:
            messages.error(
                self.request, "You do not have stored shipping addresses")
            return redirect("core:checkout")


# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         u_form = ProfileUpdateForm(request.POST, instance=request.user)
#     #   p_form = ProfileUpdateForm(request.POST,
#     #                              request.FILES,
#     #                              instance=request.user.profile)
#         if u_form.is_valid():
#             # and p_form.is_valid():
#             u_form.save()
#     #     p_form.save()
#         messages.success(request, 'Your account has been updated!')
#         # to avoid re-post request to the page(if reached to reander it will re-post)
#         return redirect('edit-profile')
#     else:
#         u_form = ProfileUpdateForm(instance=request.user)
#         # p_form = ProfileUpdateForm(instance=request.user.profile)

#         context = {
#             'form': u_form
#             # 'p_form': p_form
#         }

#     return render(request, 'user/edit-profile.html', context)
