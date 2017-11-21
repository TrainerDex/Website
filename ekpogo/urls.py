from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from trainer.views import index as welcome

api_v01_patterns = [
    url(r"^enrollment/", include('enrollment.urls', namespace="enrollment")),
    url(r"^gyms/", include('gyms.urls', namespace="gyms")),
]

urlpatterns = [
    url(r"^api/0.1/", include(api_v01_patterns, namespace="api_v01")),
    url(r"^api/admin/", admin.site.urls),
    url(r"^api/trainer/", include('trainer.urls', namespace="trainer")),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^$', welcome),
]

admin.site.site_title = "TrainerDex Admin"
