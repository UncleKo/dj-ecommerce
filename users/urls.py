from django.urls import path
from .views import *

app_name = 'user'

urlpatterns = [

    path('shipping-address/<int:pk>/update',
         ShippingAddressUpdateView.as_view(), name='shipping-address-update'),
    path('<int:pk>/edit-profile/',
         ProfileUpdateView.as_view(), name='edit-profile')

]
