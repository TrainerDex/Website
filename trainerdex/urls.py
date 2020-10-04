from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken import views

from core import sitemaps
from core.views import SettingsView
from pokemongo.views import SetUpProfileViewStep2, SetUpProfileViewStep3


urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "base": sitemaps.BaseSitemap,
                "country": sitemaps.LeaderboardCountrySitemap,
                "trainers": sitemaps.TrainerSitemap,
                "communities": sitemaps.LeaderboardCommunitySitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("api/v1/", include("pokemongo.api.v1.urls")),
    path("api/admin/", admin.site.urls),
    path("api/token-auth/", views.obtain_auth_token),
    path("api/ajax_select/", include("ajax_select.urls")),
    path("help/", include("helpdesk.urls")),
    path("accounts/settings", SettingsView, name="account_settings"),
    path("accounts/profile/setup", SetUpProfileViewStep2, name="profile_set_up"),
    path("accounts/profile/first_update", SetUpProfileViewStep3, name="profile_first_post"),
    path("accounts/", include("allauth.urls")),
    path("", include("pokemongo.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

admin.site.site_title = "TrainerDex"
admin.site.site_header = _("{site_name} Admin").format(site_name=admin.site.site_title)
