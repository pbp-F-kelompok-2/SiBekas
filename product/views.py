from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Category, Product, ProductLike

PRODUCTS_PER_PAGE = 12


def index(request):
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .with_like_info(request.user)
    )

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__icontains=query)
        )

    active_category = None
    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    ).filter(product_count__gt=0)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": categories,
        "active_category": active_category,
        "category_slug": category_slug,
        "query": query,
        "page_range": paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1),
        "page_url_prefix": f"?{querystring}&page=" if querystring else "?page=",
    }
    return render(request, "product/list.html", context)


def detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "seller")
        .prefetch_related("images")
        .with_like_info(request.user),
        slug=slug,
        is_active=True,
    )
    related_products = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .select_related("category")
        .with_like_info(request.user)[:4]
    )
    context = {
        "product": product,
        "images": product.images.all(),
        "related_products": related_products,
    }
    return render(request, "product/detail.html", context)


def _wants_json(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _redirect_back(request, product):
    next_url = request.POST.get("next") or request.headers.get("referer")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect(product.get_absolute_url())


@require_POST
def toggle_like(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    if not request.user.is_authenticated:
        message = "Masuk terlebih dahulu untuk menyukai produk."
        if _wants_json(request):
            return JsonResponse({"login_required": True, "message": message}, status=401)
        messages.info(request, message)
        return _redirect_back(request, product)

    like, created = ProductLike.objects.get_or_create(user=request.user, product=product)
    if not created:
        like.delete()

    if _wants_json(request):
        return JsonResponse({"liked": created, "like_count": product.likes.count()})
    return _redirect_back(request, product)