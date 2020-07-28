from django.urls import path
# from .views import HomeView, ItemDetailView, CartView, CheckoutView, BillingAddressView, OrderSummaryView, PaymentView, add_to_cart, remove_from_cart, remove_single_item_from_cart, confirm_order, PrimaryShippingAddress
from .views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('item/create/', ItemCreateView.as_view(), name='item-create'),
    path('item/<slug>/', ItemDetailView.as_view(), name='item'),
    path('item/<slug>/update', ItemUpdateView.as_view(), name='item-update'),
    path('shopping-cart/', CartView.as_view(), name='shopping-cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('billing-address/', BillingAddressView.as_view(), name='billing-address'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),

    path('order-list', OrderListView.as_view(), name='order-list'),
    #     path('user/<int:pk>/order-list',
    #          UserOrderListView.as_view(), name='user-order-list'),
    path('order-history',
         UserOrderListView.as_view(), name='user-order-list'),

    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('confirm-order/', confirm_order, name='confirm-order'),

    path('order-dispatched/<int:pk>', order_dispatched, name='order-dispatched'),

]
