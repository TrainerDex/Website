from django.contrib import admin

from community.models import Community, CommunityMembershipDiscord


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):

    search_fields = ('name','short_description', 'handle')
    autocomplete_fields = ['memberships_personal', 'memberships_discord']
    actions = [sync_members]


@admin.register(CommunityMembershipDiscord)
class CommunityMembershipDiscordAdmin(admin.ModelAdmin):

    autocomplete_fields = ['community', 'discord']
