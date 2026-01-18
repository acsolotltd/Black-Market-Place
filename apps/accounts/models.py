from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)




class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=150)

    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional contact number"
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country of residence"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def nick(self):
        (a, b) = self.full_name.split()
        return f"{a[0]}{b[0]}".upper()

    def get_short_name(self):
        return self.full_name.split()[0]

    def get_user(self):
        return self.self.email.split("@")[0]

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

class VendorProfile(models.Model):
    """
    Represents an Afrimarket vendor (artisan, herbalist, or seller).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name="User Account"
    )
    shop_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)

    # Optional social links / contact info
    website = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Marketplace stats
    rating = models.FloatField(default=0.0)
    followers = models.ManyToManyField(
        User,
        related_name='following_vendors',
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Vendor activity
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "1. Vendor Profile"
        verbose_name_plural = "Vendor Profiles"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Automatically generate slug from shop_name
        if not self.slug:
            self.slug = slugify(self.shop_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.shop_name

    def get_absolute_url(self):
        return reverse('accounts:public-profile', kwargs={'slug': self.slug})

    @property
    def products(self):
        """Return all products belonging to this vendor."""
        return self.user.products.filter(is_active=True)

    @property
    def orders(self):
        """Return all orders that include this vendor's products."""
        from orders.models import OrderItem
        return OrderItem.objects.filter(product__vendor=self.user)
