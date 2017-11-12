"""ekpogo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from ajax_select import urls as ajax_select_urls

api_v0_1_patterns = [
    url(r"^enrollment/", include('enrollment.urls', namespace="enrollment")),
    url(r"^gyms/", include('gyms.urls', namespace="gyms")),
    url(r"", include('trainer.urls.0.1', namespace="trainerdex")),
]

api_v0_2_patterns = [
    url(r"", include('trainer.urls.1.0', namespace="trainerdex")),
]

urlpatterns = [
    url(r"^api/0.1/", include(api_v0_1_patterns, namespace="api_v01")),
    url(r"^api/0.2/", include(api_v0_2_patterns, namespace="api_v02")),
    url(r"^api/admin/", admin.site.urls),
    url(r"^api/trainer/", include('trainer.urls.0.1', namespace="trainer")), # legacy url scheme
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^accounts/', include('allauth.urls')),
]