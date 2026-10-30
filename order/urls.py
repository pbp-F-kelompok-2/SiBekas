from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    path("", views.index, name="index"),
    path("checkout/", views.checkout, name="checkout"),
    path("seller/", views.seller_dashboard, name="seller_dashboard"),
    path("shipping/destinations/", views.destinations, name="destinations"),
    path("shipping/quotes/", views.shipping_quotes, name="shipping_quotes"),
    path("<uuid:order_id>/", views.detail, name="detail"),
    path("<uuid:order_id>/status/", views.update_status, name="update_status"),
]
