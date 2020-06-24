from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="shipping_addresses")
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    primary = models.BooleanField(default=False)

    def __str__(self):
        # return self.user.username
        return f"{self.street_address}, {self.city}, {self.state} {self.zip} {self.country}"

    # def get_absolute_url(self):
    #     return reverse("user:update-shipping-address", kwargs={
    #         'pk': self.pk
    #     })


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="billing_addresses")
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default="CA")
    zip = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip} {self.country}"
