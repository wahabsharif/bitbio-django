from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def account(request):
    return render(request, "account.html")


def registration(request):
    from .countries import COUNTRIES

    return render(request, "registration.html", {"countries": COUNTRIES})
