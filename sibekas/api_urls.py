"""Checkpoint 1: live read endpoints for every module, plus mobile authentication."""

from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cart.api_views import MyCartAPI
from order.api_views import MyOrderDetailAPI, MyOrderListAPI
from product.api_views import CategoryListAPI, ProductDetailAPI, ProductListAPI
from profiles.api_views import FavoriteListAPI, LoginAPI, LogoutAPI, MyProfileAPI
from review.api_views import ReviewListAPI

app_name = "api"


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response({"name": "SiBekas API", "version": "v1", "checkpoint": 1,
                     "modules": ["products/", "profile/", "cart/", "orders/", "reviews/"]})


urlpatterns = [
    path("", api_root, name="root"),
    path("auth/login/", LoginAPI.as_view(), name="login"),
    path("auth/logout/", LogoutAPI.as_view(), name="logout"),
    path("products/", ProductListAPI.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailAPI.as_view(), name="product-detail"),
    path("categories/", CategoryListAPI.as_view(), name="category-list"),
    path("profile/", MyProfileAPI.as_view(), name="profile"),
    path("profile/favorites/", FavoriteListAPI.as_view(), name="favorites"),
    path("cart/", MyCartAPI.as_view(), name="cart"),
    path("orders/", MyOrderListAPI.as_view(), name="order-list"),
    path("orders/<uuid:pk>/", MyOrderDetailAPI.as_view(), name="order-detail"),
    path("reviews/", ReviewListAPI.as_view(), name="review-list"),
]
