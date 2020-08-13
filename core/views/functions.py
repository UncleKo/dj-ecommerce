from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils import timezone
from django.db.models import F
from django.core.mail import send_mail
from django.template.loader import render_to_string

from ..models import Item, OrderItem, Order, Payment, SiteInfo


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
            f'{request.user.last_name}様, お買い上げありがとうございます。',
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
        messages.warning(request, "既にお気に入りに追加されてます。")
    else:
        request.user.fav_items.add(item)
        messages.success(request, "商品がお気に入りに追加されました。")
        # return redirect("core:fav-items")
    # return redirect(request.META['HTTP_REFERER'])
    # ↑だとログイン強制後ログインページに戻る不都合が生じる
    return redirect("core:item", slug=slug)


@login_required
def remove_from_fav_items(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.user.fav_items.filter(slug=slug):
        request.user.fav_items.remove(item)
        messages.success(request, "商品がお気に入りから外されました。")
    else:
        messages.warning(request, "この商品はお気に入りに入ってません。")
    return redirect("core:item", slug=slug)
