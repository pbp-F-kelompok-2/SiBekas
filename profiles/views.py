from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm
from django.contrib.auth.models import User

def index(request):
    return render(
        request,
        "module_placeholder.html",
        {"module_name": "Profile / User"},
    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
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