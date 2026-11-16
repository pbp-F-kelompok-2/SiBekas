from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import NotAuthenticated

from .models import Review
from .serializers import ReviewSerializer


class ReviewQuerySerializer(serializers.Serializer):
    product = serializers.IntegerField(min_value=1, required=False)
    mine = serializers.BooleanField(default=False)


class ReviewListAPI(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = ReviewQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        values = query.validated_data
        reviews = Review.objects.select_related("user", "product")
        if values["mine"]:
            if not self.request.user.is_authenticated:
                raise NotAuthenticated("Masuk untuk melihat ulasanmu.")
            reviews = reviews.filter(user=self.request.user)
        if "product" in values:
            reviews = reviews.filter(product_id=values["product"])
        return reviews.order_by("-created_at", "-pk")
