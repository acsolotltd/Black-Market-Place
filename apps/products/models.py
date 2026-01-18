from django.db import models
from django.conf import settings
#from apps.products.models import Product
from apps.accounts.models import VendorProfile
from django.apps import apps
#Product = apps.get_model('products', 'Product')
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def get_absolute_url(self):
        return  reverse('products:category-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class Product(models.Model):
    vendor = models.ForeignKey(VendorProfile, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    popularity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)   # ✅ ADD
    updated_at = models.DateTimeField(auto_now=True)        # ✅ ADD
    
    def discounted_price(self):
        return self.price - self.discount

    def percentage_discount(self):
        return self.discounted_price() * 100 / self.price

    def get_absolute_url(self):
        return  reverse('products:product_detail', kwargs={'product_slug': self.slug})
        
    class Meta:
        ordering = ['-created_at']  # sensible default

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField()  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ - {self.product.name}"
