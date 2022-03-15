from django.urls import path
from .views import (HomeView, ItemDetailView, ItemDetailView, checkout, add_to_cart, remove_from_cart, OrderSummaryView,remove_single_item_from_cart,add_voucher, CheckoutView, faq)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name = 'HomeView'),
    #path('product/', ItemDetailView, name = 'product-page'),
    path('checkout/', CheckoutView.as_view(), name = 'checkout'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('add-voucher/', add_voucher, name='add-voucher'),
    path('faq/', faq, name='faq')


]