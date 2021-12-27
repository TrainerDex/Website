from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from community.models import Community
from community.discord.models import DiscordCommunity


@admin.register(Community)
class CommunityAdmin(SimpleHistoryAdmin):

    search_fields = ("external_uuid", "name", "description", "handle")
    autocomplete_fields = ["memberships"]


@admin.register(DiscordCommunity)
class DiscordCommunityAdmin(SimpleHistoryAdmin):

    search_fields = ("id", "external_uuid", "name", "description")
