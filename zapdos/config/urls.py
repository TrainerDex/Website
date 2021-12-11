"""TrainerDex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core import sitemaps
from core.views import PrivacyView, SettingsView, TermsView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token-auth/", views.obtain_auth_token),
    path("api/ajax_select/", include("ajax_select.urls")),
    path("legal/privacy/", PrivacyView, name="privacy"),
    path("legal/terms/", TermsView, name="terms"),
    path("settings/", SettingsView, name="account_settings"),
    path("accounts/", include("allauth.urls")),
    path("", include("pokemongo.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

admin.site.site_title = "TrainerDex"
admin.site.site_header = _("{site_name} Admin").format(site_name=admin.site.site_title)
