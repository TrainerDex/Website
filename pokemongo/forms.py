from django.utils.translation import gettext_lazy as _
from form_utils.forms import BetterModelForm
from pokemongo.models import Update, Trainer
from pokemongo.shortcuts import UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES


class UpdateForm(BetterModelForm):
    class Meta:
        model = Update
        fieldsets = [
            (
                "main",
                {
                    "fields": [
                        "trainer",
                        "update_time",
                        "data_source",
                        "double_check_confirmation",
                        "total_xp",
                        "pokemon_info_stardust",
                        "pokedex_caught",
                        "pokedex_seen",
                        "gymbadges_total",
                        "gymbadges_gold",
                    ]
                    + list(UPDATE_FIELDS_BADGES),
                    "legend": _("Main"),
                    "classes": ["is-active"],
                },
            ),
            ("badges", {"fields": UPDATE_FIELDS_TYPES, "legend": _("Type Medals")}),
        ]


class RegistrationFormTrainer(BetterModelForm):
    class Meta:
        model = Trainer
        fields = (
            "start_date",
            "faction",
            "statistics",
            "verification",
        )


class RegistrationFormUpdate(UpdateForm):
    class Meta:
        model = Update
        fieldsets = [
            (
                "main",
                {
                    "fields": [
                        "trainer",
                        "update_time",
                        "data_source",
                        "screenshot",
                        "double_check_confirmation",
                        "total_xp",
                        "pokemon_info_stardust",
                        "pokedex_caught",
                        "pokedex_seen",
                        "gymbadges_total",
                        "gymbadges_gold",
                    ]
                    + list(UPDATE_FIELDS_BADGES),
                    "legend": _("Main"),
                    "classes": ["is-active"],
                },
            ),
            ("badges", {"fields": UPDATE_FIELDS_TYPES, "legend": _("Type Medals")}),
        ]
