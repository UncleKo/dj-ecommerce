from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit

from users.models import ShippingAddress, BillingAddress

# CATEGORY_CHOICES = (
#     ('L', 'PC'),
#     ('P', 'Parts'),
#     ('G', 'Green'),
#     ('F', 'Furniture')
# )


LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

PAYMENT_CHOICES = (
    ('C', 'クレジットカード'),
    ('B', '銀行振込')
    # ('P', 'PayPal'),
)

DELIVERY_TIME = (
    ('', '指定なし'),
    ('A', '午前中'),
    ('B', '0pm-2pm'),
    ('C', '2pm-4pm'),
    ('D', '4pm-6pm'),
    ('E', '6pm-8pm')
)


class Inquiry(models.Model):
    subject = models.CharField(
        max_length=100, verbose_name="件名(任意)", null=True, blank=True)
    name = models.CharField(
        max_length=100, verbose_name="お名前(任意)", null=True, blank=True)
    email = models.EmailField(verbose_name="メールアドレス")
    content = models.TextField(verbose_name="お問い合わせ内容")

    class Meta:
        verbose_name_plural = 'お問い合わせ'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="カテゴリー")
    order = models.IntegerField(verbose_name="メニュー順番", default=1)

    class Meta:
        verbose_name_plural = 'カテゴリー'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:category-list")

    def published_items(self):
        return self.items.filter(draft=False)


class Item(models.Model):
    title = models.CharField(max_length=100, verbose_name="商品名")
    price = models.IntegerField(verbose_name="価格")
    discount_price = models.IntegerField(
        blank=True, null=True, verbose_name="セール価格")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 related_name="items", null=True, blank=True, verbose_name="カテゴリー(option)")
    label = models.CharField(choices=LABEL_CHOICES,
                             max_length=2, blank=True, null=True, verbose_name="レーベル")
    slug = models.SlugField(blank=True, null=True, verbose_name="URL末尾")
    description = models.TextField(blank=True, null=True, verbose_name="商品説明")
    stock = models.IntegerField(blank=True, null=True, verbose_name="在庫数")
    featured = models.BooleanField(default=False)
    draft = models.BooleanField(default=False, verbose_name="非公開")
    fav_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="fav_items", blank=True)
    image = models.ImageField(blank=True, verbose_name="メイン画像")
    image_large = ImageSpecField(source="image",
                                 processors=[ResizeToFit(1280, 1280)],
                                 format='JPEG'
                                 )

    image_medium = ImageSpecField(source='image',
                                  processors=[ResizeToFit(700, 700)],
                                  format="JPEG",
                                  options={'quality': 80}
                                  )

    image_small = ImageSpecField(source='image',
                                 processors=[ResizeToFit(250, 250)],
                                 format="JPEG",
                                 options={'quality': 80}
                                 )

    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFit(75, 75)],
                                     format="JPEG",
                                     options={'quality': 80}
                                     )

    class Meta:
        verbose_name_plural = '商品'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:item", kwargs={
            'slug': self.slug
        })

    # slugを自動的に作成
    def save(self, *args, **kwargs):
        # 作成時のみ（後でTitleが変わっても、URL変わらないように）
        if not self.id:
            self.slug = slugify(self.title)
        super(Item, self).save(*args, **kwargs)

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'pk': self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'pk': self.pk
        })

    def get_add_to_fav_items_url(self):
        return reverse("core:add-to-fav-items", kwargs={
            'pk': self.pk
        })

    def get_remove_from_fav_items_url(self):
        return reverse("core:remove-from-fav-items", kwargs={
            'pk': self.pk
        })


# class Variation(models.Model):
#     item = models.ForeignKey(
#         Item, on_delete=models.CASCADE, related_name="variations")
#     name = models.CharField(max_length=50)  # size

#     class Meta:
#         unique_together = (
#             ('item', 'name')
#         )

#     def __str__(self):
#         return self.name

# class ItemVariation(models.Model):
#     variation = models.ForeignKey(
#         Variation, on_delete=models.CASCADE, related_name="item_variations")
#     value = models.CharField(max_length=50)  # S, M, L

#     class Meta:
#         unique_together = (
#             ('item', 'name')
#         )

#     def __str__(self):
#         return self.name

class SizeOption(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="size_option")
    value = models.CharField(max_length=50)
    stock = models.IntegerField(blank=True, null=True, verbose_name="在庫数")
    # attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('item', 'value')
        ),
        verbose_name_plural = '商品サイズ'

    def __str__(self):
        return self.value


class ColorOption(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="color_option")
    value = models.CharField(max_length=50)  # S, M, L
    # stock = models.IntegerField(blank=True, null=True, verbose_name="在庫数")
    # attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('item', 'value')
        ),
        verbose_name_plural = '商品カラー'

    def __str__(self):
        return self.value


class OrderItem(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    # item_variations = models.ManyToManyField(ItemVariation)
    quantity = models.IntegerField(default=0)
    # size = models.CharField(max_length=50, blank=True, null=True)
    # color = models.CharField(max_length=50, blank=True, null=True)
    color = models.ForeignKey(
        ColorOption, on_delete=models.SET_NULL, blank=True, null=True)
    size = models.ForeignKey(
        SizeOption, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'カート内各商品'

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="orders")
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    dispatched = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'users.ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'users.BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment_option = models.CharField(
        choices=PAYMENT_CHOICES, max_length=2, blank=True, null=True)
    delivery_time = models.CharField(
        choices=DELIVERY_TIME, max_length=2, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'カート内全商品/注文済注文'

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_postage(self):
        total = self.get_total()
        site_info = Site.objects.get_current().siteinfo
        if site_info.free_shippment_line:
            if total > site_info.free_shippment_line:
                return 0
            else:
                return site_info.shipping_fee
        else:
            return site_info.shipping_fee

    def to_free_postage(self):
        site_info = Site.objects.get_current().siteinfo
        if site_info.free_shippment_line:
            return Site.objects.get_current().siteinfo.free_shippment_line - self.get_total()

    def get_total_w_postage(self):
        return self.get_total() + self.get_postage()

    def get_order_dispatched(self):
        return reverse("core:order-dispatched", kwargs={
            'pk': self.pk
        })


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Stripe'

    def __str__(self):
        return self.user.username


class SiteInfo(models.Model):
    site = models.OneToOneField(
        Site, verbose_name='Site', on_delete=models.PROTECT)
    title = models.CharField('ショップ名', max_length=255, default='Store Title')
    free_shippment_line = models.IntegerField(
        verbose_name='送料無料最低価格', null=True, blank=True)
    shipping_fee = models.IntegerField(
        verbose_name='送料', default=0)
    order_history_paginate_by = models.IntegerField(
        default=5, verbose_name="購入履歴1ページ表示数")
    order_list_paginate_by = models.IntegerField(
        default=5, verbose_name="注文管理1ページ表示数")
    # item_list_paginate_by = models.IntegerField(
    #     default=10, verbose_name="商品管理1ページ表示数")
    # category_list_paginate_by = models.IntegerField(
    #     default=10, verbose_name="カテゴリー別リスト1ページ表示数")
    # fav_items_paginate_by = models.IntegerField(
    #     default=10, verbose_name="お気に入りリスト1ページ表示数")

    class Meta:
        verbose_name_plural = 'サイト設定'

    # def get_absolute_url(self):
    #     return reverse("core:siteinfo", kwargs={
    #         'site_id': self.site.site_id
    #     })

# def create_default_site_info(sender, **kwargs):
#     site = Site.objects.get(pk=settings.SITE_ID)
#     SiteInfo.objects.get_or_create(site=site)
