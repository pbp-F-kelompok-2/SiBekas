"""Root URL configuration for SiBekas."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.views.static import serve

from .views import health_check

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("health/", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("products/", include("product.urls")),
    path("profile/", include("profiles.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("order.urls")),
    path("reviews/", include("review.urls")),
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),

]
