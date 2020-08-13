from django.shortcuts import render


def SettingsView(request):
    return render(request, "account/account_settings.html")
