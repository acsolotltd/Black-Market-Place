from django.contrib import admin
from .models import  Product, ProductImage, Category
# Register your models here.
#admin.site.register(Category)
#admin.site.register(Product)

'''
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
'''

# admin.py
from django.contrib import admin
from .models import Product, ProductImage

# models.py

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # number of extra blank forms to display

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1  # number of extra blank forms to display

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ('name', 'slug')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 
'category', 'price')  # assuming you have a name and price field
