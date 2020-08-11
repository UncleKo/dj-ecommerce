from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit

from users.models import ShippingAddress, BillingAddress

CATEGORY_CHOICES = (
    ('L', 'PC'),
    ('P', 'Parts'),
    ('G', 'Green'),
    ('F', 'Furniture')
)


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


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=2)
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField()
    stock = models.IntegerField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)
    fav_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="fav_items", blank=True)
    image = models.ImageField(blank=True)
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
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_fav_items_url(self):
        return reverse("core:add-to-fav-items", kwargs={
            'slug': self.slug
        })

    def get_remove_from_fav_items_url(self):
        return reverse("core:remove-from-fav-items", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

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

    # def get_absolute_url(self):
    #     return reverse("core:siteinfo", kwargs={
    #         'site_id': self.site.site_id
    #     })

# def create_default_site_info(sender, **kwargs):
#     site = Site.objects.get(pk=settings.SITE_ID)
#     SiteInfo.objects.get_or_create(site=site)
