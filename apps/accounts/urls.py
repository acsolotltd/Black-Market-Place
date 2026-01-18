from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
   path('login/', views.htmx_login, name='login'),
    path('register/', views.register_view, name='register'),
path('vendor-register/', views.register_view, name='vendor-register'),
path("vendor/<slug:slug>/", views.vendor_public_profile, name="public-profile"),
    path('profile/', views.profile_view, name='profile'),
path('validate-email/', views.validate_email, name='validate-email'),
    path('validate-shop-name/', views.validate_shop_name, name='validate-shop-name'),
]


urlpatterns += [
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('validate_name/', views.validate_name, name='validate_name'),
    path('delete_image/<int:pk>/', views.delete_image, name='delete_image'),
    path('reorder_images/<int:pk>/', views.reorder_images, name='reorder_images'),
]
