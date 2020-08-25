
# if order_item.item.stock == 0:
#     messages.warning(request, "在庫がありません。")
# else:
#     order_qs = Order.objects.filter(
#         user=request.user,
#         ordered=False
#     )
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item
#         if order.items.filter(item__slug=item.slug).exists():
#             # stockが設定されてる場合
#             if order_item.item.stock:
#                 if order_item.quantity < order_item.item.stock:
#                     # order_item.quantity += 1
#                     # # To avoid a race condition:  2 people click "Add to cart" at the same time or a user clicks very fast that the first request isn't finished.
#                     order_item.quantity = F('quantity') + 1
#                     order_item.save()
#                     messages.info(request, "商品の数量が変更されました。")
#                 else:
#                     messages.warning(
#                         request, "在庫が不足しています。")
#             # stockが設定されてれない場合
#             else:
#                 # order_item.quantity += 1
#                 order_item.quantity = F('quantity') + 1
#                 order_item.save()
#                 messages.info(request, "商品の数量が変更されました。")

#         else:
#             order.items.add(order_item)
#             messages.info(request, "商品がカートに入りました。")

#     else:
#         ordered_date = timezone.now()
#         order = Order.objects.create(
#             user=request.user, ordered_date=ordered_date)
#         order.items.add(order_item)
#         messages.info(request, "商品がカートに入りました。")

# return redirect("core:shopping-cart")


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
        messages.info(request, "カートは空です。")
    return redirect("core:item", slug=slug)


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
        messages.info(request, "カートは空です。")
    return redirect("core:item", slug=slug)
