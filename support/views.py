﻿# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect

def FAQView(request):
	return render(request, 'help/faq.html')