from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def SettingsView(request: HttpRequest) -> HttpResponse:
    return render(request, "account/account_settings.html")
