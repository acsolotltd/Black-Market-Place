# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VendorProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('full_name', 'email', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ( 'email', 'full_name', 'is_staff')
    ordering = ('email',)


admin.site.register(VendorProfile)
