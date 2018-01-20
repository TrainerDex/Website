# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from ajax_select import urls as ajex_select_urls
from website.views import *
from trainer import urls as TrainerURLS
from support import urls as SupportURLS
from trainer.views import RegistrationView

api_v1_patterns = [
    url('', include(TrainerURLS.REST, namespace="trainer_api")),
#    url(r'^gyms/', include('raids.urls', namespace="raid_enrollment")),
]

urlpatterns = [
    url(r'^api/v1/', include(api_v1_patterns, namespace="api_v1")),
    url(r'^api/admin/', admin.site.urls),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^ajax_select/', include(ajex_select_urls)),
    url(r'^accounts/settings', SettingsView, name='account_settings'),
    url(r'^accounts/signup/$', RegistrationView, name='account_signup'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^tools/rosetta/', include('rosetta.urls')),
    url(r'^$', IndexView, name='home'),
    url(r'^communities/$', Status410),
    url(r'^help/', include(SupportURLS, namespace='help')),
    url('', include(TrainerURLS.HTML)),
]

admin.site.site_title = "TrainerDex Admin"
