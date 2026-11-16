from django.db.models import Q
from rest_framework import generics, permissions

from .models import Category, Product
from .serializers import CategorySerializer, ProductFilterSerializer, ProductSerializer


class ProductListAPI(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        filters = ProductFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        values = filters.validated_data
        products = Product.objects.select_related("category", "seller").prefetch_related("images")
        if values.get("q"):
            products = products.filter(Q(name__icontains=values["q"]) | Q(description__icontains=values["q"]))
        for parameter, field in [("category", "category__slug"), ("condition", "condition"),
                                 ("min_price", "price__gte"), ("max_price", "price__lte")]:
            if parameter in values:
                products = products.filter(**{field: values[parameter]})
        return products.order_by("-created_at", "-pk")


class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category", "seller").prefetch_related("images")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.order_by("name", "pk")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
