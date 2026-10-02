from django.urls import path

from . import views

app_name = "product"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("<slug:slug>/like/", views.toggle_like, name="toggle_like"),
]
