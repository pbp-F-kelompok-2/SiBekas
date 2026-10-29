from django.urls import path

from . import views

app_name = "product"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("create/", views.create, name="create"),
    path("<slug:slug>/edit/", views.update, name = "update"),
    path("<slug:slug>/delete/", views.delete, name = "delete"),
]
