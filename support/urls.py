# -*- coding: utf-8 -*-
from django.conf.urls import url
from support.views import FAQView

urlpatterns = [
    url(r'^faq$', FAQView, name='faq'),
]
