from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path('cart-items/', views.get_cart, name='cart-items'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.cart_view, name='cart'),
    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('remove-item/<int:item_id>/', views.remove_item, name='remove_item'),
    path('checkout/', views.checkout_view, name='checkout'),  # To be implemented
path('checkout/', views.checkout_view, name='checkout'),
    path('checkout-process/', views.checkout_process, name='checkout_process'),
    path('cart-partial/', views.cart_partial, name='cart_partial'),
]
