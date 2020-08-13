from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.authtoken import views
from core.views import SettingsView
from pokemongo.views import SetUpProfileViewStep2, SetUpProfileViewStep3
from core import sitemaps

from django.utils.translation import gettext_lazy as _

urlpatterns = [
    url(
        r"^sitemap\.xml$",
        sitemap,
        {
            "sitemaps": {
                "base": sitemaps.BaseSitemap,
                "continent": sitemaps.LeaderboardContinentSitemap,
                "country": sitemaps.LeaderboardCountrySitemap,
                "region": sitemaps.LeaderboardRegionSitemap,
                "trainers": sitemaps.TrainerSitemap,
                "Communities": sitemaps.LeaderboardCommunitySitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += [
    url(r"^api\/v1\/", include("pokemongo.api.v1.urls")),
    url(r"^api\/admin\/", admin.site.urls),
    url(r"^api-token-auth\/", views.obtain_auth_token),
    url(r"^api\/ajax_select\/", include("ajax_select.urls")),
    url(r"^help\/", include("helpdesk.urls")),
    url(r"^accounts\/settings\/?$", SettingsView, name="account_settings"),
    url(r"^accounts\/profile/setup\/?$", SetUpProfileViewStep2, name="profile_set_up"),
    url(
        r"^accounts\/profile/first_update\/?$",
        SetUpProfileViewStep3,
        name="profile_first_post",
    ),
    url(r"^accounts\/", include("allauth.urls")),
    url(r"^tools\/rosetta\/", include("rosetta.urls")),
    url(
        r"^$",
        RedirectView.as_view(pattern_name="trainerdex:leaderboard", permanent=True),
        name="home",
    ),
    url("", include("pokemongo.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]

admin.site.site_title = "TrainerDex"
admin.site.site_header = _("{site_name} Admin").format(site_name=admin.site.site_title)
