from django.urls import reverse
from django.shortcuts import render
from django.core.cache import cache

#@cache_page(60 * 15)  # 15 minutes
def landing_page(request):
    """
    Main landing page.
    Fully server-rendered, SEO-friendly.
    """
    return render(request, "core/landing.html")
'''

from django.shortcuts import render
from django.http import HttpResponseBadRequest

def explore_preview(request):
    """
    HTMX partial: category preview cards.
    Only responds to HTMX requests.
    """
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("HTMX requests only")

    return render(
        request,
        "core/partials/explore_preview.html",
    )


'''

from django.shortcuts import render
from apps.products.models import Category
from django.core.cache import cache

def explore_preview(request):
    categories = cache.get("categories")
    if not categories:
        categories = Category.objects.prefetch_related('product_set').all()[:6]
        cache.set("categories", categories)
    return render(request, 'partials/_category_card.html', {'categories': categories})
