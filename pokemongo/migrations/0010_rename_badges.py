# Generated by Django 4.0.5 on 2022-06-02 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pokemongo", "0009_remove_timezone_choices"),
    ]

    operations = [
        migrations.RenameField(
            model_name="update",
            old_name="badge_battle_attack_won",
            new_name="battle_attack_won",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_battle_training_won",
            new_name="battle_training_won",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_berries_fed",
            new_name="berries_fed",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_big_magikarp",
            new_name="big_magikarp",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_buddy_best",
            new_name="buddy_best",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_capture_total",
            new_name="capture_total",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_challenge_quests",
            new_name="challenge_quests",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_evolved_total",
            new_name="evolved_total",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_great_league",
            new_name="great_league",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="gymbadges_gold",
            new_name="gym_gold",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_hatched_total",
            new_name="hatched_total",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_hours_defended",
            new_name="hours_defended",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_legendary_battle_won",
            new_name="legendary_battle_won",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_master_league",
            new_name="master_league",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_max_level_friends",
            new_name="max_level_friends",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_photobomb",
            new_name="photobomb",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pikachu",
            new_name="pikachu",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries",
            new_name="pokedex_entries",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen2",
            new_name="pokedex_entries_gen2",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen3",
            new_name="pokedex_entries_gen3",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen4",
            new_name="pokedex_entries_gen4",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen5",
            new_name="pokedex_entries_gen5",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen6",
            new_name="pokedex_entries_gen6",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen7",
            new_name="pokedex_entries_gen7",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokedex_entries_gen8",
            new_name="pokedex_entries_gen8",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokemon_caught_at_your_lures",
            new_name="pokemon_caught_at_your_lures",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokemon_purified",
            new_name="pokemon_purified",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_pokestops_visited",
            new_name="pokestops_visited",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_raid_battle_won",
            new_name="raid_battle_won",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_raids_with_friends",
            new_name="raids_with_friends",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_rocket_giovanni_defeated",
            new_name="rocket_giovanni_defeated",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_rocket_grunts_defeated",
            new_name="rocket_grunts_defeated",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_7_day_streaks",
            new_name="seven_day_streaks",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_small_rattata",
            new_name="small_rattata",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_total_mega_evos",
            new_name="total_mega_evos",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_trading",
            new_name="trading",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_trading_distance",
            new_name="trading_distance",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_travel_km",
            new_name="travel_km",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_bug",
            new_name="type_bug",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_dark",
            new_name="type_dark",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_dragon",
            new_name="type_dragon",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_electric",
            new_name="type_electric",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_fairy",
            new_name="type_fairy",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_fighting",
            new_name="type_fighting",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_fire",
            new_name="type_fire",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_flying",
            new_name="type_flying",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_ghost",
            new_name="type_ghost",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_grass",
            new_name="type_grass",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_ground",
            new_name="type_ground",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_ice",
            new_name="type_ice",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_normal",
            new_name="type_normal",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_poison",
            new_name="type_poison",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_psychic",
            new_name="type_psychic",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_rock",
            new_name="type_rock",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_steel",
            new_name="type_steel",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_type_water",
            new_name="type_water",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_ultra_league",
            new_name="ultra_league",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_unique_mega_evos",
            new_name="unique_mega_evos",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_unique_pokestops",
            new_name="unique_pokestops",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_unique_raid_bosses_defeated",
            new_name="unique_raid_bosses_defeated",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_unown",
            new_name="unown",
        ),
        migrations.RenameField(
            model_name="update",
            old_name="badge_wayfarer",
            new_name="wayfarer",
        ),
    ]
