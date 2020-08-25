from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils import timezone
from django.db.models import F
from django.core.mail import send_mail
from django.template.loader import render_to_string

from ..models import Item, OrderItem, Order, Payment, SiteInfo
from ..forms import ItemOptionForm


@login_required
def add_to_fav_items(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.user.fav_items.filter(pk=pk):
        messages.warning(request, "既にお気に入りに追加されてます。")
    else:
        request.user.fav_items.add(item)
        messages.success(request, "商品がお気に入りに追加されました。")
        return redirect("user:fav-items")
    # return redirect(request.META['HTTP_REFERER'])
    # ↑だとログイン強制後ログインページに戻る不都合が生じる
    return redirect("core:item", slug=slug)


@login_required
def remove_from_fav_items(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.user.fav_items.filter(pk=pk):
        request.user.fav_items.remove(item)
        messages.success(request, "商品がお気に入りから外されました。")
    else:
        messages.warning(request, "この商品はお気に入りに入ってません。")
    # itemページ、お気に入りリスト、２箇所あることと、削除できる時点で既にログインしてるので。
    return redirect(request.META['HTTP_REFERER'])


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemOptionForm(item, request.POST or None)
    if form.is_valid():
        color = form.cleaned_data.get('color_option')
        size = form.cleaned_data.get('size_option')
        quantity = int(form.cleaned_data.get('quantity'))
    # else:
    #     color = None
    #     size = None

    if item.stock == 0:
        messages.warning(request, "在庫がありません。")
        return redirect('core:item', slug=item.slug)
    elif item.stock and quantity > item.stock:
        messages.warning(request, "在庫が不足しています。")
        return redirect('core:item', slug=item.slug)

    # Stock以下の数量、あるいはStockが設定されてない場合
    else:

        # order_item, created = OrderItem.objects.get_or_create(
        order_item_qs = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False,
        )

        # for v in variations: #[1,4]
        #     order_item_qs = order_item_qs.filter(
        #         item_variations_exact=v
        #     )
        order_item_qs = order_item_qs.filter(
            color=color,
            size=size
        )

        if order_item_qs.exists():
            # order_item = order_item_qs.first()
            # order_item.quantity += quantity
            # if item.stock and order_item.quantity >= item.stock:
            #     messages.warning(request, "在庫が不足しています。")
            # else:
            #     order_item.save()
            #     messages.info(request, "商品の数量が変更されました。")
            messages.warning(request, "商品は既にカートに入ってます。数量を確認/調整して下さい。")
            return redirect("core:shopping-cart")
        else:
            order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                ordered=False
            )
            # order_item.item_variations.add([1,4])
            # order_item.item_variations.add(*variations)
            order_item.color = color
            order_item.size = size

        if order_item.size and order_item.size.stock == 0:
            messages.warning(request, "在庫がありません。")
            order_item.delete()
            return redirect('core:item', slug=item.slug)
        elif order_item.size and order_item.size.stock and quantity > order_item.size.stock:
            messages.warning(request, "在庫が不足しています。")
            order_item.delete()
            return redirect('core:item', slug=item.slug)
        # elif order_item.color.stock and order_item.quantity >= order_item.color.stock:
        #     messages.warning(request, "在庫が不足しています。")
        else:
            # order_item.quantity += 1
            # order_item.quantity = F('quantity') + 1
            order_item.quantity = quantity
            order_item.save()
            order_qs = Order.objects.filter(
                user=request.user,
                ordered=False
            )
            if order_qs.exists():
                order = order_qs[0]
                # check if the order item is in the order
                # if not order.items.filter(item__id=item.id).exists():
                if not order.items.filter(id=order_item.id).exists():
                    order.items.add(order_item)
                    messages.info(request, "商品がカートに入りました。")

            else:
                ordered_date = timezone.now()
                order = Order.objects.create(
                    user=request.user, ordered_date=ordered_date)
                order.items.add(order_item)
                messages.info(request, "商品がカートに入りました。")

    return redirect("core:shopping-cart")


@login_required
def add_single_item_to_cart(request, pk):
    order_item = get_object_or_404(OrderItem, pk=pk)

    # if order_item.item.stock == 0:
    #     messages.warning(request, "在庫がありません。")
    if order_item.item.stock and order_item.quantity >= order_item.item.stock:
        messages.warning(request, "在庫が不足しています。")
    elif order_item.size and order_item.size.stock and order_item.quantity >= order_item.size.stock:
        messages.warning(request, "在庫が不足しています。")
    # elif order_item.color.stock and order_item.quantity >= order_item.color.stock:
    #     messages.warning(request, "在庫が不足しています。")
    else:
        # order_item.quantity += 1
        order_item.quantity = F('quantity') + 1
        order_item.save()
        messages.info(request, "商品の数量が変更されました。")

    return redirect("core:shopping-cart")


@login_required
def remove_from_cart(request, pk):
    order_item = get_object_or_404(OrderItem, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    # if order_qs.exists():
    order = order_qs[0]
    # if order.items.filter(id=order_item.id).exists:
    order.items.remove(order_item)
    order_item.delete()
    messages.info(request, "商品がカートから外されました。")
    return redirect("core:shopping-cart")
    # else:
    #     messages.info(request, "この商品はカートに入ってません。")
    # else:
    #     messages.info(request, "カートは空です。")
    # return redirect("core:item", slug=slug)


@login_required
def remove_single_item_from_cart(request, pk):
    order_item = get_object_or_404(OrderItem, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    order = order_qs[0]
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order.items.remove(order_item)
        order_item.delete()
    messages.info(request, "商品の数量が変更されました。")
    return redirect("core:shopping-cart")


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
        messages.error(request, "カートは空です。")
        return render(request, 'core/shopping-cart.html')


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
