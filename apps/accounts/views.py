from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User #, Address
from apps.products.models import Product, ProductImage
from apps.orders.models import Cart  as Order, CartItem
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # or home

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return HttpResponse("Logged in successfully!", status=200)
        else:
            return HttpResponse("Invalid credentials", status=400)
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return HttpResponse("Passwords do not match.", status=400)
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already registered.", status=400)

        #user = User.objects.create_user(email=email, full_name=full_name, password=password1, is_active=False)
        user = User.objects.create_user(email=email, full_name=full_name, password=password1, is_active=False)

        # TODO: send verification email with token
        return HttpResponse("Registered successfully! Check your email to verify your account.", status=200)
    return render(request, 'accounts/register.html')


def vendor_register_view(request): 
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return HttpResponse("Passwords do not match.",)
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already registered.")

        user = User.objects.create_user(email=email, full_name = full_name)

        # TODO: send verification email with token
        return HttpResponse("Registered successfully! Checck your email")
    return render(request, 'accounts/vendor-register.html')

def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'orders': orders})

def vendor_dashboard(request):
    vendor = request.vendor_profile
    #print(vendor)
    vendor_products = Product.objects.filter(vendor=vendor)
    orders = Order.objects.filter(items__product__vendor=vendor).distinct().order_by('-created_at')
    return render(request, 'accounts/vendor_dashboard.html', {
        'vendor_products': vendor_products,
        'orders': orders
    })




from django.views.decorators.http import require_POST
from django.http import HttpResponse

@require_POST
def add_product(request):
    vendor = request.user.vendor_profile
    name = request.POST.get('name')
    price = request.POST.get('price')
    category = request.POST.get('category')
    description = request.POST.get('description')
    image = request.FILES.get('image')

    product = Product.objects.create(
        vendor=vendor,
        name=name,
        price=price,
        category_id=category,
        description=description,
        image=image
    )

    # Return rendered product card for HTMX
    return render(request, 'partials/_vendor_product.html', {'product': product})





from django import forms

class ProductForm(forms.ModelForm):
    #images = forms.FileField(widget=forms.FileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'vendor']

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor_profile
            product.save()
            images = request.FILES.getlist('images')
            for image in images:
                img = ProductImage.objects.create(image=image)
                product.images.add(img)
            return render(request, 'success.html')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


def validate_name(request):
    name = request.POST.get('name')
    if len(name) < 3:
        return HttpResponse('<div class="text-red-500 text-sm">Name must be at least 3 chars</div>')
    return HttpResponse('')

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            images = request.FILES.getlist('images')
            if len(images) > 5:
                return HttpResponse('<div class="text-red-500">Max 5 images allowed</div>')
            for image in images:
                if image.size > 2 * 1024 * 1024:
                    return HttpResponse('<div class="text-red-500">Image too large (max 2MB)</div>')
                img = Image.objects.create(image=image)
                product.images.add(img)
            return render(request, 'success.html')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

def delete_image(request, pk):
    image = Image.objects.get(id=pk)
    image.delete()
    return HttpResponse('')

def reorder_images(request, pk):
    product = Product.objects.get(id=pk)
    ids = json.loads(request.body)
    product.images.clear()
    for id in ids:
        image = Image.objects.get(id=id)
        product.images.add(image)
    return HttpResponse('')


'''
def validate_name(request):
    name = request.POST.get('name')
    if len(name) < 3:
        return HttpResponse('<div class="text-red-500 text-sm">Name must be at least 3 chars</div>')
    return HttpResponse('')

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            images = request.FILES.getlist('images')
            for image in images:
                img = Image.objects.create(image=image)
                product.images.add(img)
            return render(request, 'success.html')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def delete_image(request, pk):
    image = Image.objects.get(id=pk)
    image.delete()
    return HttpResponse('')

def reorder_images(request, pk):
    product = Product.objects.get(id=pk)
    ids = json.loads(request.body)
    product.images.clear()
    for id in ids:
        image = Image.objects.get(id=id)
        product.images.add(image)
    return HttpResponse('')
'''

import json
from django.db.models import Sum, F
from datetime import timedelta, date
import json
from decimal import Decimal


def convert_decimals(data):
    if isinstance(data, dict):
        return {k: convert_decimals(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimals(i) for i in data]
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data


def vendor_dashboard(request):
    vendor = request.user.vendor_profile
    vendor_products = Product.objects.filter(vendor=vendor)
    orders = Order.objects.filter(items__product__vendor=vendor).distinct().order_by('-created_at')

    # Prepare sales data for analytics
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in reversed(range(7))]
    daily_sales = []

    for d in last_7_days:
        #sum(item.total_price() for item in self.items.all())
	#from django.db.models import F, Sum
        total = orders.filter(created_at__date=d).aggregate(
	sum=Sum(F('items__product__price') * F('items__quantity')))['sum'] or 0
        #total = orders.filter(created_at__date=d).aggregate(sum=Sum('total_price'))['sum'] or 0
        daily_sales.append({'date': d.strftime('%b %d'), 'total': total})

    # Top 5 products by quantity sold
    top_products_qs = CartItem.objects.filter(product__vendor=vendor).values('product__name') \
                    .annotate(sales=Sum('quantity')).order_by('-sales')[:5]
    top_products = [{'name': p['product__name'], 'sales': p['sales']} for p in top_products_qs]

    sales_data = {'daily_sales': daily_sales, 'top_products': top_products}

    #sales_data_json = {k: str(v) if isinstance(v, Decimal) else v for k, v in sales_data.items()}
    sales_data_json = convert_decimals(sales_data)
    return render(request, 'accounts/vendor_dashboard.html', {
        'vendor_products': vendor_products,
        'orders': orders,
        'sales_data': json.dumps(sales_data_json)
    })



@login_required
def update_price(request, pk):
    product = get_object_or_404(Product, id=pk, vendor=request.user)
    product.price = request.POST["price"]
    product.save()
    return render(request, "_product_row.html", {"product": product})






from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

@require_POST
def htmx_login(request):
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    if not email or not password:
        return JsonResponse({'error': 'Please fill out all fields.'}, status=400)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({'error': 'Invalid email or password.'}, status=400)
    if not user.is_active:
        return JsonResponse({'error': 'Account is inactive.'}, status=400)

    login(request, user)
    # If HTMX, we can redirect using HX-Redirect header
    response = JsonResponse({'success': True})
    response['HX-Redirect'] = '/'  # Redirect to landing page or dashboard
    return response




from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from .models import VendorProfile

User = get_user_model()

@require_GET
def validate_email(request):
    email = request.GET.get('email', '').strip()
    if not email:
        return JsonResponse({'message': ''})
    if User.objects.filter(email=email).exists():
        return JsonResponse({'message': 'Email already taken'}, status=400)
    return JsonResponse({'message': 'Email is available'})

@require_GET
def validate_shop_name(request):
    shop_name = request.GET.get('shop_name', '').strip()
    if not shop_name:
        return JsonResponse({'message': ''})
    if VendorProfile.objects.filter(shop_name__iexact=shop_name).exists():
        return JsonResponse({'message': 'Shop name already taken'}, status=400)
    return JsonResponse({'message': 'Shop name is available'})




# vendors/views.py

from django.shortcuts import get_object_or_404, render
from .models import VendorProfile
from apps.products.models import Product

def vendor_public_profile(request, slug):
    vendor = get_object_or_404(
        VendorProfile,
        slug=slug,
        is_active=True
    )

    products = Product.objects.filter(
        vendor=vendor,
        is_active=True
    ).select_related("category")

    return render(request, "vendors/public_profile.html", {
        "vendor": vendor,
        "products": products,
    })
