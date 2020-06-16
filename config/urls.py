from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from rest_framework.authtoken import views

# from core.views import *
# from trainerdex.views import SetUpProfileViewStep2, SetUpProfileViewStep3

urlpatterns = [
    url(r'^admin\/', admin.site.urls),
    # url(r'^api\/oauth\/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api\/v1\/', include('trainerdex.api.v1.urls')),
    url(r'^api-token-auth\/', views.obtain_auth_token),
    # url(r'^accounts\/settings\/?$', SettingsView, name='account_settings'),
    # url(r'^accounts\/', include('allauth.urls')),
    # url(r'^tools\/rosetta\/', include('rosetta.urls')), # Confirm this works in Django 3, change URL.
    url('', include('trainerdex.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]

admin.site.site_title = "TrainerDex"
admin.site.site_header = f"{admin.site.site_title} Admin"
