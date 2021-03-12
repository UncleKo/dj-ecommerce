from django.urls import path
# from .views import HomeView, ItemDetailView, CartView, CheckoutView, BillingAddressView, OrderSummaryView, PaymentView, add_to_cart, remove_from_cart, remove_single_item_from_cart, confirm_order, PrimaryShippingAddress
from .views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('shopping-cart/', CartView.as_view(), name='shopping-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('billing-address/', BillingAddressView.as_view(), name='billing-address'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),

    path('add-to-cart/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('add-single-item-to-cart/<int:pk>/',
         add_single_item_to_cart, name='add-single-item-to-cart'),
    path('remove-from-cart/<int:pk>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<int:pk>/',
         remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('add-to-fav-items/<int:pk>', add_to_fav_items, name='add-to-fav-items'),
    path('remove-from-fav-items/<int:pk>',
         remove_from_fav_items, name='remove-from-fav-items'),

    path('confirm-order/', confirm_order, name='confirm-order'),
    path('order-dispatched/<int:pk>', order_dispatched, name='order-dispatched'),

    #     path('email', email_test, name='email-view'),
    path('inquiry', InquiryCreateView.as_view(), name='inquiry'),

    path('myadmin', MyAdminView.as_view(), name='myadmin'),
    path('order-list', OrderListView.as_view(), name='order-list'),
    path('siteinfo/<pk>/edit', SiteInfoUpdateView.as_view(), name='siteinfo'),

    path('item-list/', ItemListView.as_view(), name='item-list'),
    path('item/create/', add_item, name='item-create'),
    path('item/<slug>/', ItemDetailView.as_view(), name='item'),
    path('item/<slug>/edit', update_item, name='item-update'),
    path('item/<slug>/delete', ItemDeleteView.as_view(), name='item-delete'),

    path('category-list/', CategoryListView.as_view(), name='category-list'),
    path('category/create/', CategoryCreateView.as_view(), name='category-create'),
    path('category/<int:pk>/edit',
         CategoryUpdateView.as_view(), name='category-update'),
    path('category/<int:pk>/delete',
         CategoryDeleteView.as_view(), name='category-delete'),

    path('category/<str:category_name>/',
         CategoryItemListView.as_view(), name='category-pages'),
]
