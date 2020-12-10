from django.utils.translation import pgettext
from form_utils.forms import BetterModelForm
from pokemongo.models import Update, Trainer
from pokemongo.shortcuts import STANDARD_MEDALS, BATTLE_HUB_STATS, UPDATE_FIELDS_TYPES


class UpdateForm(BetterModelForm):
    class Meta:
        model = Update
        fieldsets = [
            (
                "stats",
                {
                    "fields": [
                        "trainer",
                        "update_time",
                        "data_source",
                        "double_check_confirmation",
                        "total_xp",
                        "pokedex_caught",
                        "pokedex_seen",
                        "gymbadges_total",
                        "gymbadges_gold",
                    ],
                    "legend": pgettext("profile_category_stats", "Stats"),
                },
            ),
            (
                "medals",
                {
                    "fields": STANDARD_MEDALS,
                    "legend": pgettext("profile_category_medals", "Medals"),
                },
            ),
            (
                "battle_hub",
                {
                    "fields": BATTLE_HUB_STATS,
                    "legend": pgettext("battle_hub_category_league", "GO Battle League"),
                },
            ),
            (
                "types",
                {"fields": UPDATE_FIELDS_TYPES, "legend": pgettext("pokemon_info_type", "Type")},
            ),
        ]


class TrainerForm(BetterModelForm):
    class Meta:
        model = Trainer
        fields = (
            "start_date",
            "faction",
            "statistics",
            "trainer_code",
            "leaderboard_country",
            "verification",
        )
