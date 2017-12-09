from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from ajax_select import urls as ajex_select_urls
from website.views import *

api_v0_2_patterns = [
    url(r"", include('trainer.urls', namespace="trainerdex")),
]

urlpatterns = [
    url(r"^api/0.2/", include(api_v0_2_patterns, namespace="api_v02")),
    url(r"^api/admin/", admin.site.urls),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^ajax_select/', include(ajex_select_urls)),
    url(r'^$', index, name='home'),
    url(r'^communities/', communities, name='communities'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html'), name='user_profile'),
]

admin.site.site_title = "TrainerDex Admin"
