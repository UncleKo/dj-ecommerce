from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from core.boost import DynamicRedirectMixin

from django.contrib.sites.models import Site
from ..models import Item, Order, SiteInfo, Category


class MyAdminView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, View):

    def get(self, *args, **kwargs):
        return render(self.request, "myadmin/index.html")

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class SiteInfoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SiteInfo
    fields = ['title', 'free_shippment_line', 'shipping_fee',
              'order_history_paginate_by', 'order_list_paginate_by']
    template_name = 'myadmin/siteinfo_form.html'
    # success_url = reverse_lazy('core:siteinfo')
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        form.instance.site_id = 1
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'myadmin/category_list.html'
    paginate_by = 2

    def get_queryset(self):
        return Category.objects.all().order_by('order')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, DynamicRedirectMixin, CreateView):
    model = Category
    fields = ['name', 'order']
    template_name = 'myadmin/category_form.html'
    # success_url = reverse_lazy('core:category-list')

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
    template_name = 'myadmin/category_form.html'
    # success_url = reverse_lazy('core:category-list')

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
    template_name = 'myadmin/category_confirm_delete.html'
    # success_url = reverse_lazy('core:category-list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = self.object.items.all()
        return context


class ItemListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Item
    fields = ['title', 'price', 'discount_price', 'category',
              'description', 'stock', 'featured', 'image', 'draft']
    template_name = 'myadmin/item_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Item
    fields = ['title', 'price', 'discount_price', 'category',
              'description', 'stock', 'featured', 'image', 'draft']
    template_name = 'myadmin/item_form.html'
    success_url = reverse_lazy('core:item-list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ['title', 'price', 'discount_price', 'category',
              'description', 'stock', 'featured', 'image', 'draft', 'slug']
    template_name = 'myadmin/item_form.html'

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
    template_name = 'myadmin/item_confirm_delete.html'
    success_url = reverse_lazy('core:item-list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


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


# def email_test(request):
#     order = Order.objects.get(pk=3)
#     context = {
#         'order': order
#     }
#     return render(request, 'parts/email.html', context)
