from django.contrib import admin
from django.contrib.sites.models import Site
from .models import Item, OrderItem, Order, Payment, ShippingAddress, BillingAddress, SiteInfo, Category, Inquiry


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'stock', 'featured', 'id']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'ordered']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'id', 'ordered_date']


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'primary',
                    'street_address', 'city', 'state', 'zip', 'id']


class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'primary',
                    'street_address', 'city', 'state', 'zip', 'id']


class SiteInfoInline(admin.StackedInline):
    model = SiteInfo


class SiteAdmin(admin.ModelAdmin):
    inlines = [SiteInfoInline]


admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)

admin.site.register(SiteInfo)
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)

admin.site.register(Inquiry)
