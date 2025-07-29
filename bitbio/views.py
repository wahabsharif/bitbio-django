from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def account(request):
    return render(request, "account.html")
