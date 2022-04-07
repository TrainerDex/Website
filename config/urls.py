from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView
from rest_framework.authtoken import views

from core import sitemaps
from core.views import PrivacyView, SettingsView, TermsView
from pokemongo.views import EditProfileView, health_check

app_name = "trainerdex"
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "base": sitemaps.BaseSitemap,
                "trainers": sitemaps.TrainerSitemap,
                "communities": sitemaps.LeaderboardCommunitySitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("api/admin/", admin.site.urls),
    path("api/v1/", include("pokemongo.api.v1.urls")),
    path("api/token-auth/", views.obtain_auth_token),
    path("api/ajax_select/", include("ajax_select.urls")),
    path("api/health/", health_check),
    path("legal/privacy/", PrivacyView, name="privacy"),
    path("legal/terms/", TermsView, name="terms"),
    path("settings/", SettingsView, name="account_settings"),
    path("settings/profile/", EditProfileView, name="profile_edit"),
    path("accounts/", include("allauth.urls")),
    path("", include("pokemongo.urls")),
    path("silk/", include("silk.urls", namespace="silk")),
    path("docs/", include("docs.urls")),
]

admin.site.site_title = "TrainerDex"
admin.site.site_header = _("{site_name} Admin").format(site_name=admin.site.site_title)
