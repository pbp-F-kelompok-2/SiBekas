from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Avg
from .models import Category, Product
from .forms import ProductForm
from profiles.models import Favorite
from django.core.cache import cache

PRODUCTS_PER_PAGE = 12

def seller_required(view):
    def wrapper(request, slug):
        product = get_object_or_404(Product, slug = slug)
        if product.seller != request.user:
            return render(request, "product/403.html", {"product": product}, status = 403)
        return view(request, product)
    return wrapper

def index(request):
    products = Product.objects.select_related("category")
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(name__icontains=query)

    if request.GET.get("mine") and request.user.is_authenticated:
        products = products.filter(seller=request.user)

    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    condition = request.GET.get("condition", "")

    if condition:
        products = products.filter(condition=condition)

    min_price = request.GET.get("min_price", "")
    if min_price.isdigit():
        products = products.filter(price__gte=min_price)

    max_price = request.GET.get("max_price", "")
    if max_price.isdigit():
        products = products.filter(price__lte=max_price)

    sort = request.GET.get("sort", "")
    if sort == "cheap":
        products = products.order_by("price")
    elif sort == "expensive":
        products = products.order_by("-price")

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "page": page_obj,
        "categories": categories,
        "category_slug": category_slug,
        "query": query,
        "page_url_prefix": f"?{querystring}&page=" if querystring else "?page=",
        "conditions": Product.CONDITION_CHOICES,
    }
    return render(request, "product/list.html", context)

def detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
    )

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            product=product,
        ).exists()

    related_products = (
        Product.objects.filter(category = product.category)
        .exclude(pk=product.pk)[:20]
    )
    context = {
        "product": product,
        "images": product.images.all(),
        "related_products": related_products,
        "is_favorite": is_favorite,
        "reviews": product.reviews.select_related("user").order_by("-created_at"),
        "average_rating": product.reviews.aggregate(average=Avg("rating"))["average"],
    }
    return render(request, "product/detail.html", context)


@login_required
@seller_required
def update(request, product):
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Produk berhasil diperbaharui")
        return redirect(product)
    return render(request, "product/form.html", {"form": form, "title": "Ubah produk"})

@login_required
@require_POST
@seller_required
def delete(request, product):
    product.delete()
    messages.success(request, "Produk berhasil dihapus")
    return redirect("product:index")

def rate_limit(limit, seconds):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            key = f"rate:{view.__name__}:{request.user.pk}"
            cache.add(key, 0, seconds)
            if cache.incr(key) > limit:
                messages.error(request, "Terlalu banyak permintaan")
                return redirect("product:index")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
@rate_limit(5, 60)
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user #kesambung dengan pembuatnya
            product.save()

            messages.success(
                request,
                "Produk berhasil ditambahkan!"
            )
            return redirect("profile:index")
    else:
        form = ProductForm()

    return render(
        request,
        "product/create.html",
        {"form": form},
    )

@login_required
@require_POST
@rate_limit(5, 60)
def bulk_delete(request):
    ids = [i for i in request.POST.getlist("ids") if i.isdigit()]
    Product.objects.filter(pk__in=ids,seller=request.user).delete()
    messages.success(request, "Produk terpilih berhasil dihapus")
    return redirect("/products/?mine=1")


