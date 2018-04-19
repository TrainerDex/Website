# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from ajax_select import urls as ajex_select_urls
from website.views import *
from trainer import urls as TrainerURLS
from support import urls as SupportURLS
from trainer.views import SetUpProfileViewStep2, SetUpProfileViewStep3

api_v1_patterns = [
    url('', include(TrainerURLS.REST, namespace="trainer_api")),
]

urlpatterns = [
    url(r'^api/v1/', include(api_v1_patterns, namespace="api_v1")),
    url(r'^api/admin/', admin.site.urls),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^ajax_select/', include(ajex_select_urls)),
    url(r'^accounts/settings/$', SettingsView, name='account_settings'),
    url(r'^accounts/profile/setup$', SetUpProfileViewStep2, name='profile_set_up'),
    url(r'^accounts/profile/first_update$', SetUpProfileViewStep3, name='profile_first_post'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^tools/rosetta/', include('rosetta.urls')),
    url(r'^$', RedirectView.as_view(pattern_name='leaderboard', permanent=False), name='home'),
    url(r'^communities/$', Status410),
    url(r'^help/', include(SupportURLS, namespace='help')),
    url('', include(TrainerURLS.HTML)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]

admin.site.site_header = "TrainerDex Admin"
admin.site.site_title = "TrainerDex Admin"
