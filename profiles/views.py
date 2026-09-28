from django.shortcuts import render


def index(request):
    return render(request, "module_placeholder.html", {"module_name": "Profile / User"})
