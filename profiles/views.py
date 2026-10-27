from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile
from product.models import Product
from django.utils.http import url_has_allowed_host_and_scheme


@login_required
def index(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    form = ProfileForm(instance=profile)

    my_products = Product.objects.filter(
        seller=request.user
    ).select_related("category")

    return render(
        request,
        "profiles/index.html",
        {
            "profile": profile,
            "form": form,
            "my_products": my_products,
            "total_listings": my_products.count(),
        },
    )

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect("profile:index")
    else:
        form = RegisterForm()

    return render(request, "profiles/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            user = authenticate(
                request,
                username=user.username,
                password=password,
            )

        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next", "")
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect("profile:index")

        return render(
            request,
            "profiles/login.html",
            {"error": "Email atau password salah."},
        )

    return render(request, "profiles/login.html")


def logout_view(request):
    logout(request)
    return redirect("profile:login")


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            return redirect("profile:index")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "profiles/edit_profile.html",
        {"form": form},
    )

class PasswordResetView(auth_views.PasswordResetView):
    template_name = "profiles/password_reset_form.html"
    email_template_name = "profiles/password_reset_email.html"
    subject_template_name = "profiles/password_reset_subject.txt"
    success_url = reverse_lazy("profile:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "profiles/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "profiles/password_reset_confirm.html"
    success_url = reverse_lazy("profile:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "profiles/password_reset_complete.html"