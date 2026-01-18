from django.urls import path
from . import views
app_name = 'products'


from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('featured/', views.featured_products, name='featured'),
    path('categories/', views.load_categories, name='load_categories'),
    path('load-more/<int:category_id>/', views.load_more_products, name='load_more_products'),
    #path('categories/', views.load_categories, name='load_categories'),
    path('category/<int:category_id>/products/', views.category_products, name='category_products'),
    path('category/<slug:slug>/', views.category_detail, name='category-detail'),
    path('category/<slug:slug>/products/', views.category_products_htmx, name='category-products-htmx'),
    path('category/<slug:slug>/filters/', views.category_filters_partial, name='category-filters-partial'),

#path('', views.ProductListView.as_view(), name='all-products'),
path("all-products/", views.AllProductsView.as_view(), name="all-products"),

    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    path('search/', views.search_products, name='search-products'),
# products/urls.py
path("vendor/products/new/", views.product_create, name="product_create"),
path("vendor/products/<int:pk>/edit/", views.product_update, name="product_update"),
path("quick-view/<slug:slug>/", views.product_quick_view, name="quick-view"),

]
