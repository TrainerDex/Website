from django.contrib import admin

from community.models import Community


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):

    search_fields = ('name', 'short_description', 'handle')
    readonly_fields = ('handle')
    autocomplete_fields = ['members']
