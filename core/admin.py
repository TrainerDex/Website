import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
from django.contrib import admin
from django.utils.safestring import mark_safe
from core.models import DiscordGuild

@admin.register(DiscordGuild)
class DiscordGuildAdmin(admin.ModelAdmin):
    fields = ('id','data_prettified','cached_date')
    readonly_fields = fields
    search_fields = ('id', 'data__name')
    
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
