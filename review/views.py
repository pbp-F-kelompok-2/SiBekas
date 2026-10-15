from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg

from product.models import Product

from .forms import ReviewForm
from .models import Review


@login_required
def index(request):
    reviewed_product_ids = Review.objects.filter(
        user=request.user
    ).values_list("product_id", flat=True)

    average_rating = Review.objects.filter(
        user=request.user
    ).aggregate(
        average=Avg("rating")
    )["average"]

    products_to_review = Product.objects.exclude(
        id__in=reviewed_product_ids
    )

    my_reviews = Review.objects.filter(
        user=request.user
    ).select_related("product")

    return render(
        request,
        "review/index.html",
        {
            "products_to_review": products_to_review,
            "my_reviews": my_reviews,
            "average_rating": average_rating,
        },
    )


@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(
        user=request.user,
        product=product,
    ).exists():
        return redirect("review:index")

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

            return redirect("review:index")
    else:
        form = ReviewForm()

    return render(
        request,
        "review/create.html",
        {
            "form": form,
            "product": product,
        },
    )

@login_required
def update_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user,
    )

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            review = form.save(commit=False)
            review.edited = True
            review.save()
            return redirect("review:index")

    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "review/update.html",
        {
            "form": form,
            "review": review,
        },
    )

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user,
    )

    if request.method == "POST":
        review.delete()
        return redirect("review:index")

    return render(
        request,
        "review/delete.html",
        {
            "review": review,
        },
    )