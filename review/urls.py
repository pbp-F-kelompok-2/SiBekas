from django.urls import path

from . import views

app_name = "review"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/<int:product_id>/", views.create_review, name="create"),
    path("update/<int:review_id>/", views.update_review, name="update"),
    path("delete/<int:review_id>/", views.delete_review, name="delete"),
]