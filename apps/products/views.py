from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
render, 
get_object_or_404,
redirect
)
from django.core.cache import cache
from .models import (
Category, 
Product, 
ProductImage, 
Review
)

def search_products(request):
    query = request.GET.get('q', '')
    all_products = cache.get("all_products")
    if not all_products:
        all_products = Product.objects.all()
    products = all_products.filter(name__icontains=query)[:10]
    return render(request, 'partials/_search_results.html', {'products': products})




def load_categories(request):
    categories = Category.objects.prefetch_related('product_set').all()
    return render(request, 'partials/_category_card.html', {'categories': categories})

def load_more_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # Skip first 3 products since preview already loaded
    products = category.products.all()[3:10]  # Load next batch
    return render(request, 'partials/_product_card.html', {'products': products})







def category_products(request, category_id):
    cat_id = cache.get(f"category-{category_id}")
    if not cat_id:
        cat_id = get_object_or_404(Category, id=category_id)
        cache.set(f"category-{category_id}", cat_id)
    products = cache.get(f"cat-{category_id}-products")
    if not products:
        products = cat_id.product_set.all()
        cache.set(f"cat-{category_id}-products", products)
   
    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low_high':
        products = products.order_by('price')
    elif sort == 'price_high_low':
        products = products.order_by('-price')
    elif sort == 'popularity':
        # Assuming Product model has 'popularity' field or related orders count
        products = products.order_by('-popularity')
    else:
        products = products.order_by('-id')  # newest

    # Filtering by price
    price_range = request.GET.get('price_range', '')
    if price_range:
        if price_range == '0-50':
            products = products.filter(price__lte=50)
        elif price_range == '51-100':
            products = products.filter(price__gte=51, price__lte=100)
        elif price_range == '101-500':
            products = products.filter(price__gte=101, price__lte=500)
        elif price_range == '500+':
            products = products.filter(price__gte=500)

    return render(request, 'partials/_product_card.html', {'products': products})





def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    product_images = list(ProductImage.objects.filter(product=product).values())
    return render(request, 'products/product_detail.html', {
        'product': product,
        'product_images': product_images
    })

def product_reviews(request, product_id):
    reviews = Review.objects.filter(product_id=product_id).order_by('-created_at')
    return render(request, 'partials/_product_reviews.html', {'reviews': reviews})





from django.contrib.auth.decorators import login_required
from .forms import ProductForm, ProductImageFormSet

@login_required
def product_create(request):
    if not request.user.is_vendor:
        return redirect("core:home")

    if request.method == "POST":
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                product.vendor = request.user
                product.save()

                formset.instance = product
                formset.save()

            return redirect("vendor:dashboard")

    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, "products/vendor_product_form.html", {
        "form": form,
        "formset": formset,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Product
from .forms import ProductForm, ProductImageFormSet


@login_required
def product_update(request, pk):
    """
    Vendor-only product update.
    Product + images edited on one page.
    """
    if not request.user.is_vendor:
        return redirect("core:home")

    product = get_object_or_404(
        Product,
        pk=pk,
        vendor=request.user
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            instance=product
        )
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()

            return redirect("accounts:vendor_products")

    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(
        request,
        "products/vendor_product_form.html",
        {
            "form": form,
            "formset": formset,
            "product": product,
            "is_edit": True,
        },
    )


@login_required
def toggle_product(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        vendor=request.user
    )

    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])

    return HttpResponse(status=204)


@login_required
def reorder_images(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        vendor=request.user
    )

    for image_id, position in request.POST.items():
        ProductImage.objects.filter(
            id=image_id,
            product=product
        ).update(position=position)

    return HttpResponse(status=204)



from django.shortcuts import render
from .models import Product

def featured_products(request):
    featured_products = cache.get("featured_products")
    if not featured_products:
        featured_products = Product.objects.filter(is_active=True).order_by('-popularity')[:8]
        cache.set("featured_products", featured_products)
    return render(request, 'partials/_featured_products.html', {'products':featured_products})





from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 24  # Optional: page 1 loads 24 products
    queryset = Product.objects.filter(is_active=True).select_related('vendor').prefetch_related('images')


from django.views.generic import ListView
from django_htmx.http import HttpResponseClientRedirect
from .models import Product

class AllProductsView(ListView):
    model = Product
    template_name = "products/all_products.html"
    context_object_name = "products"
    paginate_by = 16

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related("vendor")
        )

    def render_to_response(self, context, **response_kwargs):
        request = self.request

        if request.headers.get("HX-Request") == "true":
            return render(
                request,
                "products/partials/_product_list.html",
                context
            )

        return super().render_to_response(context, **response_kwargs)

   
def category_products_htmx(request, slug):
    category = get_object_or_404(Category, slug=slug)
    page = request.GET.get('page', 1)
    all_products = cache.get("all_products")
    if all_products:
        all_products = Product.objects.all()
    products = all_products.filter(category=category, is_active=True).order_by('-created_at')
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(page)
    return render(request, 'partials/_category_products.html', {'products': page_obj})





from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Category, Product
from apps.accounts.models import VendorProfile  # adjust imports
import math

PAGE_SIZE = 12



from django.db.models import Prefetch, Count
from apps.accounts.models import VendorProfile

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Filtering/sorting
    sort = request.GET.get('sort', 'newest')
    products_qs = Product.objects.filter(category=category, is_active=True)

    if sort == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort == 'price_desc':
        products_qs = products_qs.order_by('-price')
    else:
        products_qs = products_qs.order_by('-created_at')

    # Pagination
    page_num = request.GET.get('page', 1)
    paginator = Paginator(products_qs.select_related('category', 'vendor'), 24)
    page_obj = paginator.get_page(page_num)

    # VENDORS: choose correct query depending on your models
    # Option 1: Product.vendor -> VendorProfile (recommended)
    vendors = VendorProfile.objects.filter(product__category=category) \
                                   .annotate(product_count=Count('product')) \
                                   .distinct().order_by('shop_name')

    # Option 2 (if your Product.vendor -> User and related_name='products'):
    # vendors = VendorProfile.objects.filter(user__products__category=category) \
    #                                .annotate(product_count=Count('user__products')) \
    #                                .distinct().order_by('shop_name')

    context = {
        'category': category,
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'vendors': vendors,
	"total": page_obj.paginator.count if page_obj else len(products_qs)
    }

    # If HTMX requested partial product HTML
    if getattr(request, 'htmx', False):
        return render(request, 'products/partials/_category_products.html', context)

    return render(request, 'products/category_detail.html', context)


def _build_product_queryset(category, params):
    """
    Build filtered queryset. Use annotate for popularity based on cartitems or orderitems.
    """
    qs = Product.objects.filter(category=category, is_active=True).select_related('vendor').prefetch_related('images')

    # price filtering
    price_min = params.get('price_min')
    price_max = params.get('price_max')
    if price_min:
        try:
            qs = qs.filter(price__gte=float(price_min))
        except (ValueError, TypeError):
            pass
    if price_max:
        try:
            qs = qs.filter(price__lte=float(price_max))
        except (ValueError, TypeError):
            pass

    # vendor filter (expects vendor id)
    vendor_id = params.get('vendor')
    if vendor_id:
        qs = qs.filter(vendor_id=vendor_id)

    # annotate popularity (number of times product appears in cartitems or orders)
    qs = qs.annotate(num_orders=Count('cartitem', distinct=True))

    # sorting
    sort = params.get('sort', 'newest')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'popularity':
        qs = qs.order_by('-num_orders', '-id')
    else:
        qs = qs.order_by('-created_at')

    return qs


def category_products_htmx(request, slug):
    """
    HTMX endpoint that returns the product cards (partial).
    Accepts query params: page, sort, price_min, price_max, vendor
    """
    category = get_object_or_404(Category, slug=slug)
    params = request.GET
    qs = _build_product_queryset(category, params)

    # pagination
    page = int(request.GET.get('page', 1))
    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(page)

    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'category': category,
    }
    return render(request, 'products/partials/_category_products.html', context)


def category_filters_partial(request, slug):
    """
    HTMX endpoint for the sidebar (useful when you want to lazy-load vendor list or stats).
    """
    category = get_object_or_404(Category, slug=slug)
    # vendors in category
    vendors = VendorProfile.objects.filter(product__category=category).distinct().order_by('shop_name')
    # aggregated counts per vendor (optional)
    vendor_counts = (
        vendors.annotate(product_count=Count('product'))
               .values('id', 'shop_name', 'product_count')
    )
    return render(request, 'products/partials/_filter_sidebar.html', {'vendors': vendor_counts, 'category': category})


def product_quick_view(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("vendor"),
        slug=slug,
        is_active=True
    )

    return render(
        request,
        "products/partials/_quick_view.html",
        {"product": product}
    )
