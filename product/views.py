from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm
from profiles.models import Favorite

PRODUCTS_PER_PAGE = 12

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
        "products": page_obj.object_list,
        "categories": categories,
        "category_slug": category_slug,
        "query": query,
        "page_range": paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1),
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
        .exclude(pk=product.pk)
    )
    context = {
        "product": product,
        "images": product.images.all(),
        "related_products": related_products,
        "is_favorite": is_favorite,
    }
    return render(request, "product/detail.html", context)


@login_required
def update(request, slug):
    product = get_object_or_404(Product, slug=slug, seller=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect(product)
    return render(request, "product/form.html", {"form": form, "title": "Ubah produk"})

@login_required
@require_POST
def delete(request, slug):
    product = get_object_or_404(Product, slug=slug, seller = request.user)
    product.delete()
    return redirect("product:index")

@login_required
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

