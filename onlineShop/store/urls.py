from django.urls import path
from .views import (
    AccountEditView,
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    ColorComparisonsView,
)

app_name = 'store'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home', HomeView.as_view(), name='home2'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart/', OrderSummaryView.as_view(), name='cart'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', 
        remove_single_item_from_cart,
        name='remove-single-item-from-cart'),
    path('checkout/payment/<payment_option>/', PaymentView.as_view(), name='payment'),

    path('account-edit', AccountEditView.as_view(), name='account-edit'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

    path('dev/colors', ColorComparisonsView.as_view(), name='color-comparisons'),
]
