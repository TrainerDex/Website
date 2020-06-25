from django.conf.urls import url
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from rest_framework.authtoken import views

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('trainerdex.api.v1.urls')),
    url(r'^api-token-auth\/', views.obtain_auth_token),
    url('', include('core.urls')),
    url('', include('trainerdex.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
