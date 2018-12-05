# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse

def SettingsView(request):
    return render(request, 'account/account_settings.html')
