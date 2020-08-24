from django.utils.translation import gettext_lazy as _
from form_utils.forms import BetterModelForm
from pokemongo.models import Update, Trainer


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
                        "badge_travel_km",
                        "badge_pokedex_entries",
                        "badge_capture_total",
                        "badge_evolved_total",
                        "badge_hatched_total",
                        "badge_pokestops_visited",
                        "badge_big_magikarp",
                        "badge_battle_attack_won",
                        "badge_battle_training_won",
                        "badge_small_rattata",
                        "badge_pikachu",
                        "badge_unown",
                        "badge_pokedex_entries_gen2",
                        "badge_raid_battle_won",
                        "badge_legendary_battle_won",
                        "badge_berries_fed",
                        "badge_hours_defended",
                        "badge_pokedex_entries_gen3",
                        "badge_challenge_quests",
                        "badge_max_level_friends",
                        "badge_trading",
                        "badge_trading_distance",
                        "badge_pokedex_entries_gen4",
                        "badge_great_league",
                        "badge_ultra_league",
                        "badge_master_league",
                        "badge_photobomb",
                        "badge_pokemon_purified",
                        "badge_photobombadge_rocket_grunts_defeated",
                        "badge_pokedex_entries_gen5",
                        "badge_pokedex_entries_gen8",
                    ],
                    "legend": _("Main"),
                    "classes": ["is-active"],
                },
            ),
            (
                "badges",
                {
                    "fields": [
                        "badge_type_normal",
                        "badge_type_fighting",
                        "badge_type_flying",
                        "badge_type_poison",
                        "badge_type_ground",
                        "badge_type_rock",
                        "badge_type_bug",
                        "badge_type_ghost",
                        "badge_type_steel",
                        "badge_type_fire",
                        "badge_type_water",
                        "badge_type_grass",
                        "badge_type_electric",
                        "badge_type_psychic",
                        "badge_type_ice",
                        "badge_type_dragon",
                        "badge_type_dark",
                        "badge_type_fairy",
                    ],
                    "legend": _("Type Medals"),
                },
            ),
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
                        "badge_travel_km",
                        "badge_pokedex_entries",
                        "badge_capture_total",
                        "badge_evolved_total",
                        "badge_hatched_total",
                        "badge_pokestops_visited",
                        "badge_big_magikarp",
                        "badge_battle_attack_won",
                        "badge_battle_training_won",
                        "badge_small_rattata",
                        "badge_pikachu",
                        "badge_unown",
                        "badge_pokedex_entries_gen2",
                        "badge_raid_battle_won",
                        "badge_legendary_battle_won",
                        "badge_berries_fed",
                        "badge_hours_defended",
                        "badge_pokedex_entries_gen3",
                        "badge_challenge_quests",
                        "badge_max_level_friends",
                        "badge_trading",
                        "badge_trading_distance",
                        "badge_pokedex_entries_gen4",
                        "badge_great_league",
                        "badge_ultra_league",
                        "badge_master_league",
                        "badge_pokemon_purified",
                        "badge_photobombadge_rocket_grunts_defeated",
                        "badge_pokedex_entries_gen5",
                        "badge_pokedex_entries_gen8",
                    ],
                    "legend": _("Main"),
                    "classes": ["is-active"],
                },
            ),
            (
                "badges",
                {
                    "fields": [
                        "badge_type_normal",
                        "badge_type_fighting",
                        "badge_type_flying",
                        "badge_type_poison",
                        "badge_type_ground",
                        "badge_type_rock",
                        "badge_type_bug",
                        "badge_type_ghost",
                        "badge_type_steel",
                        "badge_type_fire",
                        "badge_type_water",
                        "badge_type_grass",
                        "badge_type_electric",
                        "badge_type_psychic",
                        "badge_type_ice",
                        "badge_type_dragon",
                        "badge_type_dark",
                        "badge_type_fairy",
                    ],
                    "legend": _("Type Medals"),
                },
            ),
        ]
