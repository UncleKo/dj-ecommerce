from django.urls import reverse_lazy
# from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import F
# from django.urls import reverse_lazy

from ..models import Item, OrderItem, Order, Payment, SiteInfo
from ..models import CATEGORY_CHOICES
from users.models import ShippingAddress, BillingAddress
# from .boost import DynamicRedirectMixin

# Email
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context


class SiteInfoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SiteInfo
    fields = ['title', 'free_shippment_line', 'shipping_fee']
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
        if self.object.fav_users.filter(id=self.request.user.id):
            context["already_favorite"] = True
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


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            if not order.shipping_address or not order.payment_option:
                messages.warning(
                    self.request, "必要な情報をすべて記入してください。")
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
            f'商品が発送されました。',
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
                request, "必要な情報をすべて記入してください。")
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
            f'{request.user.first_name}様, お買い上げありがとうございます。',
            # f'{order.id} at {order.ordered_date}',
            msg_plain,
            'uncleko496@gmail.com',
            ['uncleko496@gmail.com', request.user.email],
            html_message=msg_html,
            # fail_silentl,
        )
        messages.success(request, "お買い上げありがとうございます。")
        return render(request, 'core/shopping-cart.html')

    except ObjectDoesNotExist:
        messages.error(request, "カートに何も入ってません。")
        return render(request, 'core/shopping-cart.html')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    if order_item.item.stock == 0:
        messages.warning(request, "在庫がありません。")
    else:
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item
            if order.items.filter(item__slug=item.slug).exists():
                # stockが設定されてる場合
                if order_item.item.stock:
                    if order_item.quantity < order_item.item.stock:
                        # order_item.quantity += 1
                        # # To avoid a race condition:  2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished.
                        order_item.quantity = F('quantity') + 1
                        order_item.save()
                        messages.info(request, "商品がカートに入りました。")
                    else:
                        messages.warning(
                            request, "在庫が不足しています。")
                # stockが設定されてれない場合
                else:
                    # order_item.quantity += 1
                    order_item.quantity = F('quantity') + 1
                    order_item.save()
                    messages.info(request, "This item quantity was updated.")

            else:
                # if order_item.item.stock:
                order.items.add(order_item)
                messages.info(request, "商品がカートに入りました。")
                # else:
                #     messages.warning(request, "在庫がありません。")

        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            # if order_item.item.stock:
            order.items.add(order_item)
            messages.info(request, "商品がカートに入りました。")
            # else:
            #     messages.warning(request, "在庫がありません。")
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
            messages.info(request, "商品がカートから外されました。")
            return redirect("core:shopping-cart")
        else:
            messages.info(request, "この商品はカートに入ってません。")
    else:
        messages.info(request, "カートに何も入ってません。")
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
            messages.info(request, "商品の数量が変更されました。")
            return redirect("core:shopping-cart")
        else:
            messages.info(request, "この商品はカートに入ってません。")
    else:
        messages.info(request, "カートに何も入ってません。")
    return redirect("core:item", slug=slug)


@login_required
def add_to_fav_items(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.user.fav_items.filter(slug=slug):
        messages.warning(request, "既にお気に入りに追加されてます")
    else:
        request.user.fav_items.add(item)
        messages.success(request, "商品がお気に入りに追加されました")
        # return redirect("core:fav-items")
    # return redirect(request.META['HTTP_REFERER'])
    # ↑だとログイン強制後ログインページに戻る不都合が生じる
    return redirect("core:item", slug=slug)


@login_required
def remove_from_fav_items(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.user.fav_items.filter(slug=slug):
        request.user.fav_items.remove(item)
        messages.success(request, "商品がお気に入りから外されました")
    else:
        messages.warning(request, "この商品はお気に入りに入ってません。")
    return redirect("core:item", slug=slug)


class FavItemsListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = "core/fav_items.html"
    context_object_name = 'fav_items'
    # paginate_by = 3
    ordering = ['-id']
    # ordering = ['?']

    def get_queryset(self):
        return Item.objects.filter(fav_users=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_choices"] = CATEGORY_CHOICES

        return context

    # def test_func(self):
    #     user = self.get_object().fav_user
    #     if self.request.user == user:
    #         return True
    #     return False
