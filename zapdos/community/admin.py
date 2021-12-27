from typing import Optional
from django.contrib import admin
from django.forms.models import ModelForm
from django.http.request import HttpRequest
from simple_history.admin import SimpleHistoryAdmin

from community.models import Community
from community.discord.models import DiscordCommunity


@admin.register(Community)
class CommunityAdmin(SimpleHistoryAdmin):
    fields = (
        "handle",
        "name",
        "description",
        "preferred_locale",
        "preferred_timezone",
        "privacy_public",
        "privacy_public_join",
    )
    search_fields = ("external_uuid", "name", "description", "handle")
    autocomplete_fields = ["memberships"]
    date_hierarchy = "updated_at"
    list_display = (
        "handle",
        "name",
        "preferred_locale",
        "preferred_timezone",
        "privacy_public",
        "privacy_public_join",
    )
    list_display_links = ("handle", "name")
    list_filter = (
        "preferred_locale",
        "privacy_public",
        "privacy_public_join",
    )
    prepopulated_fields = {"handle": ("name",)}


@admin.register(DiscordCommunity)
class DiscordCommunityAdmin(SimpleHistoryAdmin):
    search_fields = ("id", "external_uuid", "name", "description")
    date_hierarchy = "updated_at"
    list_display = (
        "handle",
        "name",
        "preferred_locale",
        "preferred_timezone",
        "privacy_public",
        "privacy_public_join",
    )
    list_display_links = ("handle", "name")
    list_filter = (
        "preferred_locale",
        "privacy_public",
        "privacy_public_join",
    )

    def get_fields(self, request: HttpRequest, obj: Optional[DiscordCommunity] = None):
        if obj:
            return (
                "handle",
                "name",
                "description",
                "preferred_locale",
                "preferred_timezone",
                "privacy_public",
                "privacy_public_join",
            )
        else:
            return (
                "id",
                "preferred_locale",
                "preferred_timezone",
                "privacy_public",
                "privacy_public_join",
            )

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[DiscordCommunity] = None):
        if obj:
            return (
                "handle",
                "name",
                "description",
            )
        else:
            return ()

    def save_model(
        self,
        request: HttpRequest,
        obj: DiscordCommunity,
        form: ModelForm,
        change: bool,
    ):
        obj.get_details_from_api()
        super().save_model(request, obj, form, change)
