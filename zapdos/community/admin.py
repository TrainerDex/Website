from django.contrib import admin

from community.models import Community


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):

    search_fields = ("name", "short_description", "handle")
    autocomplete_fields = ["memberships"]
