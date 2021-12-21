from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from pokemongo.constants import BATTLE_HUB_STATS, STANDARD_MEDALS, UPDATE_FIELDS_TYPES
from pokemongo.models import (
    BattleHubPost,
    FactionAlliance,
    GymBadgePost,
    MedalProgressPost,
)

admin.site.register(FactionAlliance)
admin.site.register(BattleHubPost)
admin.site.register(GymBadgePost)


@admin.register(MedalProgressPost)
class MedalProgressUpdateAdmin(admin.ModelAdmin):

    autocomplete_fields = ["user"]
    list_display = (
        "user",
        "total_xp",
        "created_at",
        "updated_at",
        "post_dt",
    )
    search_fields = ("user__username",)
    ordering = ("-post_dt",)
    date_hierarchy = "post_dt"

    readonly_fields = ["created_at"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "uuid",
                    "trainer",
                    "submission_date",
                    "post_dt",
                    "data_source",
                    "screenshot",
                    "double_check_confirmation",
                ]
            },
        ),
        (
            pgettext("profile_category_stats", "Stats"),
            {
                "fields": [
                    "total_xp",
                    "pokedex_caught",
                    "pokedex_seen",
                    "gymbadges_gold",
                ],
            },
        ),
        (
            pgettext("profile_category_medals", "Medals"),
            {"fields": STANDARD_MEDALS},
        ),
        (
            pgettext("battle_hub_category_league", "GO Battle League"),
            {"fields": BATTLE_HUB_STATS},
        ),
        (
            pgettext("pokemon_info_type", "Type"),
            {"fields": UPDATE_FIELDS_TYPES},
        ),
    ]
