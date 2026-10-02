from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Category, Product

PRODUCTS_PER_PAGE = 12

def index(request):
    products = Product.objects.select_related("category")
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(name__icontains=query)

    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

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
    }
    return render(request, "product/list.html", context)


def detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
    )
    related_products = (
        Product.objects.filter(category = product.category)
        .exclude(pk=product.pk)
    )
    context = {
        "product": product,
        "images": product.images.all(),
        "related_products": related_products,
    }
    return render(request, "product/detail.html", context)



