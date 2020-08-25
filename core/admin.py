from django.contrib import admin
from django.contrib.sites.models import Site
from .models import Item, OrderItem, Order, Payment, ShippingAddress, BillingAddress, SiteInfo, Category, Inquiry, SizeOption, ColorOption  # Variation, ItemVariation


# class ItemVariationAdmin(admin.ModelAdmin):
#     list_display = ['variation', 'value', 'attachment']
#     list_filter = ['variation', 'variation__item']
#     search_fields = ['value']


# class ItemVariationInlineAdmin(admin.TabularInline):
#     model = ItemVariation
#     extra = 1


# class VariationAdmin(admin.ModelAdmin):
#     list_display = ['item', 'name']
#     list_filter = ['item']
#     search_fields = ['name']
#     inlines = [ItemVariationInlineAdmin]


# class VariationInlineAdmin(admin.TabularInline):
#     model = Variation
#     extra = 1

class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ['item', 'value']
    list_filter = ['item']
    search_fields = ['value']


class SizeOptionInlineAdmin(admin.TabularInline):
    model = SizeOption
    extra = 1


class ColorOptionAdmin(admin.ModelAdmin):
    list_display = ['item', 'value']
    list_filter = ['item']
    search_fields = ['value']


class ColorOptionInlineAdmin(admin.TabularInline):
    model = ColorOption
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'stock',
                    'category', 'featured', 'draft', 'id']
    list_filter = ['category']
    search_fields = ['title']
    # inlines = [VariationInlineAdmin]
    inlines = [SizeOptionInlineAdmin, ColorOptionInlineAdmin]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'quantity', 'ordered', 'id']


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
# admin.site.register(Variation, VariationAdmin)
# admin.site.register(ItemVariation, ItemVariationAdmin)
admin.site.register(SizeOption, SizeOptionAdmin)
admin.site.register(ColorOption, ColorOptionAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)

admin.site.register(SiteInfo)
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)

admin.site.register(Inquiry)
