from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def settings(request: HttpRequest) -> HttpResponse:
    return render(request, "account/account_settings.html")


def privacy(request: HttpRequest) -> HttpResponse:
    return render(request, "privacy.html")


def terms(request: HttpRequest) -> HttpResponse:
    return render(request, "terms.html")


def service_status(request: HttpRequest) -> HttpResponse:
    return render(request, "status.html")
