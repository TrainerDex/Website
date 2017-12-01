from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from ajax_select import urls as ajex_select_urls
from website.views import *

api_v01_patterns = [
    url(r"^enrollment/", include('enrollment.urls', namespace="enrollment")),
]

urlpatterns = [
    url(r"^api/0.1/", include(api_v01_patterns, namespace="api_v01")),
    url(r"^api/admin/", admin.site.urls),
    url(r"^api/trainer/", include('trainer.urls', namespace="trainer")),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^ajax_select/', include(ajex_select_urls)),
    url(r'^$', index),
    url(r'^communities/', communities),
]

admin.site.site_title = "TrainerDex Admin"
