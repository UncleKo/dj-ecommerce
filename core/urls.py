from django.urls import path
# from .views import HomeView, ItemDetailView, CartView, CheckoutView, BillingAddressView, OrderSummaryView, PaymentView, add_to_cart, remove_from_cart, remove_single_item_from_cart, confirm_order, PrimaryShippingAddress
from .views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('shopping-cart/', CartView.as_view(), name='shopping-cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('billing-address/', BillingAddressView.as_view(), name='billing-address'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),

    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('confirm-order/', confirm_order, name='confirm-order'),

    path('primary-shipping-address/', PrimaryShippingAddress.as_view(),
         name='primary-shipping-address'),
]
