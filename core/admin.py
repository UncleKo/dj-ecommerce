from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, ShippingAddress, BillingAddress


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'id', 'ordered_date']


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'ordered']


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'city', 'state', 'zip', 'id']


class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'city', 'state', 'zip', 'id']


admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)
