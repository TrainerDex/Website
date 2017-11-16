from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
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
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html'), name='user_profile'),
]