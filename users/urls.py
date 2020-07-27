from django.urls import path
from .views import *

app_name = 'user'

urlpatterns = [

    path('profile/', ProfileView.as_view(), name='profile'),
    path('<int:pk>/edit-profile/',
         ProfileUpdateView.as_view(), name='edit-profile'),

    path('shipping-address/create/',
         ShippingAddressCreateView.as_view(), name='create-shipping-address'),
    path('shipping-address/<int:pk>/update',
         ShippingAddressUpdateView.as_view(), name='update-shipping-address'),
    path('shipping-address/<int:pk>/delete',
         ShippingAddressDeleteView.as_view(), name='delete-shipping-address'),
    path('primary-shipping-address/', PrimaryShippingAddress.as_view(),
         name='primary-shipping-address'),

]
