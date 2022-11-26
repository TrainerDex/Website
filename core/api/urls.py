from django.urls import path

from core.api.views import (
    DiscordPreferencesView,
    ServiceDetailView,
    ServiceListView,
    TestOAuthView,
    health_check,
)

app_name = "core.api"

urlpatterns = [
    path("services/", ServiceListView.as_view(), name="service_list"),
    path("services/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
    path("health/", health_check),
    path("oauth/test/", TestOAuthView.as_view()),
    path(
        "discord/preferences/",
        DiscordPreferencesView.as_view({"get": "list", "post": "create"}),
        name="discord_preferences",
    ),
    path(
        "discord/preferences/<int:pk>/",
        DiscordPreferencesView.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="discord_preferences",
    ),
]
