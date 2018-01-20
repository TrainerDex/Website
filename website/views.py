# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse

def IndexView(request):
	return render(request, 'index.html')

def Status410(request):
	return HttpResponse(status=410)

def SettingsView(request):
	return render(request, 'help/account_settings.html')
