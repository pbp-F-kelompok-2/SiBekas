from django.urls import path

from . import views

app_name = "product"

urlpatterns = [
    path("", views.index, name="index"),
    path("tambah/", views.create_product, name="create"),
    path("bulk-delete/", views.bulk_delete, name = "bulk_delete"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("<slug:slug>/edit/", views.update, name = "update"),
    path("<slug:slug>/delete/", views.delete, name = "delete"),
]
