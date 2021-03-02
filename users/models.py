from django.db import models
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.storage import default_storage as storage


### Don't miss signals.py and apps.py to produce Profile when User Created ###
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg',
                              upload_to='profile_pics', verbose_name="プロフィール画像")

    class Meta:
        verbose_name_plural = "プロフィール"

    def __str__(self):
        return f"{self.user.username} プロフィール"

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        # S3でエラー
        # img = Image.open(self.image.path)
        img = Image.open(storage.open(self.image.name))

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="shipping_addresses")
    street_address = models.CharField(max_length=100, verbose_name="番地/部屋番号")
    city = models.CharField(max_length=100, verbose_name='市区町村')
    state = models.CharField(max_length=100, verbose_name='都道府県')
    zip = models.CharField(max_length=100, verbose_name='郵便番号')
    # country = CountryField(multiple=False)
    primary = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '配送先住所'

    def __str__(self):
        return f"{self.state} {self.city} {self.street_address}"
        # return f"{self.street_address}, {self.city}, {self.state} {self.zip} {self.country}"

    # def get_absolute_url(self):
    #     # return reverse("user:profile", kwargs={
    #     #     'pk': self.user.pk
    #     # })
    #     return resolve_url('user:profile', pk=self.user.pk)
    # def get_absolute_url(self):
    #     return reverse("user:update-shipping-address", kwargs={
    #         'pk': self.pk
    #     })


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="billing_addresses")
    street_address = models.CharField(max_length=100, verbose_name="番地/部屋番号")
    city = models.CharField(max_length=100, verbose_name='市区町村')
    state = models.CharField(max_length=100, verbose_name='都道府県')
    zip = models.CharField(max_length=100, verbose_name='郵便番号')
    # country = CountryField(multiple=False)
    primary = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '請求先住所'

    def __str__(self):
        return f"{self.state} {self.city} {self.street_address}"
        # return f"{self.street_address}, {self.city}, {self.state} {self.zip} {self.country}"

    # def get_absolute_url(self):
    #     return reverse("user:profile", kwargs={
    #         'pk': self.user.pk
    #     })
