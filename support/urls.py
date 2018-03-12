# -*- coding: utf-8 -*-
from django.conf.urls import url
from support.views import *

urlpatterns = [
    url(r'^faq$', FAQView, name='faq'),
    url(r'^about$', AboutView, name='about'),
]
