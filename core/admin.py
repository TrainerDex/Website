import json
from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, ngettext
from core.models import DiscordGuild, DiscordGuildChannel, DiscordGuildRole, DiscordGuildMembership
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

def sync_members(modeladmin, request, queryset):
    for x in queryset:
        results = x.sync_members()
        for message in results['success']:
            messages.success(request, message)
        for message in results['warning']:
            messages.warning(request, message)
    
sync_members.short_description = _('Sync members with Discord')

def download_channels(modeladmin, request, queryset):
    for x in queryset:
        x.download_channels()

download_channels.short_description = _("Download channels from Discord. Currently doesn't delete them.")

@admin.register(DiscordGuild)
class DiscordGuildAdmin(admin.ModelAdmin):
    fields = ('id', 'admin', 'data_prettified', 'cached_date')
    search_fields = ('id', 'data__name')
    actions = [sync_members, download_channels]
    list_display = ('__str__', 'admin', 'cached_date')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.fields
        else:
            return [x for x in self.fields if x != 'id']
    
    def data_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.data, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    data_prettified.short_description = 'data'

@admin.register(DiscordGuildChannel)
class DiscordGuildChannelAdmin(admin.ModelAdmin):
    fields = ('guild','data_prettified','cached_date')
    readonly_fields = fields
    autocomplete_fields = ['guild']
    search_fields = ('guild', 'data__name')
    list_display = ('name', 'guild', 'cached_date')
    list_filter = ('guild', 'cached_date')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.fields
        else:
            return ('data_prettified','cached_date',)
    
    def data_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.data, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    data_prettified.short_description = 'data'

@admin.register(DiscordGuildRole)
class DiscordGuildRoleAdmin(admin.ModelAdmin):
    fields = ('guild','data_prettified','cached_date')
    readonly_fields = fields
    autocomplete_fields = ['guild']
    search_fields = ('guild', 'id')
    list_display = ('name', 'guild', 'cached_date', 'position',)
    list_filter = ('guild', 'cached_date')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.fields
        else:
            return ('data_prettified','cached_date')
    
    def data_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.data, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    data_prettified.short_description = 'data'

@admin.register(DiscordGuildMembership)
class DiscordGuildMembershipAdmin(admin.ModelAdmin):
    fields = ('guild', 'user','data_prettified','cached_date')
    readonly_fields = fields
    autocomplete_fields = ['guild', 'user']
    search_fields = ('guild', 'user', 'data__nick', 'data__user__username')
    list_display = ('user', 'guild', 'active', 'cached_date',)
    list_filter = ('guild', 'active','cached_date')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.fields
        else:
            return ('data_prettified','cached_date')
    
    def data_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.data, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    data_prettified.short_description = 'data'

admin.site.unregister(SocialAccount)
@admin.register(SocialAccount)
class SocialAccountAdmin(BaseSocialAccountAdmin):
    search_fields = ['user', 'uid']
