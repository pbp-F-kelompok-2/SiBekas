from django.urls import path

from . import views

app_name = "cart"


urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "json/",
        views.cart_json,
        name="cart_json",
    ),
    path(
        "add/",
        views.add_item,
        name="add_item",
    ),
    path(
        "bulk-delete/",
        views.bulk_delete,
        name="bulk_delete",
    ),
    path(
        "item/<int:item_id>/update/",
        views.update_item,
        name="update_item",
    ),
    path(
        "item/<int:item_id>/remove/",
        views.remove_item,
        name="remove_item",
    ),
]
