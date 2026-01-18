from django.urls import path
from .views import landing_page
from .views import explore_preview

app_name = "core"

urlpatterns = [
    path("", landing_page, name="landing"),
    path("htmx/explore-preview/", explore_preview, name="explore_preview"),
]
