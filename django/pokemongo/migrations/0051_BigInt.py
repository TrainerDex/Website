# Generated by Django 2.2.18.dev20201213213954 on 2021-09-11 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pokemongo", "0050_auto_20201213_2013"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trainer",
            name="total_goal",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_battle_attack_won",
            field=models.BigIntegerField(
                blank=True,
                help_text="Win 4000 Gym battles.",
                null=True,
                verbose_name="Battle Girl",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_battle_training_won",
            field=models.BigIntegerField(
                blank=True, help_text="Train 2000 times.", null=True, verbose_name="Ace Trainer"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_berries_fed",
            field=models.BigIntegerField(
                blank=True,
                help_text="Feed 15000 Berries at Gyms.",
                null=True,
                verbose_name="Berry Master",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_big_magikarp",
            field=models.BigIntegerField(
                blank=True, help_text="Catch 1000 big Magikarp.", null=True, verbose_name="Fisher"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_buddy_best",
            field=models.BigIntegerField(
                blank=True,
                help_text="Have 200 Best Buddies.",
                null=True,
                verbose_name="Best Buddy",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_capture_total",
            field=models.BigIntegerField(
                blank=True, help_text="Catch 50000 Pokémon.", null=True, verbose_name="Collector"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_challenge_quests",
            field=models.BigIntegerField(
                blank=True,
                help_text="Complete 2500 Field Research tasks.",
                null=True,
                verbose_name="Pokémon Ranger",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_evolved_total",
            field=models.BigIntegerField(
                blank=True, help_text="Evolve 2000 Pokémon.", null=True, verbose_name="Scientist"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_great_league",
            field=models.BigIntegerField(
                blank=True,
                help_text="Win 1000 Trainer Battles in the Great League.",
                null=True,
                verbose_name="Great League Veteran",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_hatched_total",
            field=models.BigIntegerField(
                blank=True, help_text="Hatch 2500 eggs.", null=True, verbose_name="Breeder"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_legendary_battle_won",
            field=models.BigIntegerField(
                blank=True,
                help_text="Win 2000 Legendary raids.",
                null=True,
                verbose_name="Battle Legend",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_master_league",
            field=models.BigIntegerField(
                blank=True,
                help_text="Win 1000 Trainer Battles in the Master League.",
                null=True,
                verbose_name="Master League Veteran",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_max_level_friends",
            field=models.BigIntegerField(
                blank=True,
                help_text="Become Best Friends with 20 Trainers.",
                null=True,
                verbose_name="Idol",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_photobomb",
            field=models.BigIntegerField(
                blank=True,
                help_text="Have 400 surprise encounters in GO Snapshot.",
                null=True,
                verbose_name="Cameraman",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_pikachu",
            field=models.BigIntegerField(
                blank=True, help_text="Catch 1000 Pikachu.", null=True, verbose_name="Pikachu Fan"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_pokemon_caught_at_your_lures",
            field=models.BigIntegerField(
                blank=True,
                help_text="Use a Lure Module to help another Trainer catch a Pokémon.",
                null=True,
                verbose_name="Picnicker",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_pokemon_purified",
            field=models.BigIntegerField(
                blank=True,
                help_text="Purify 1000 Shadow Pokémon.",
                null=True,
                verbose_name="Purifier",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_pokestops_visited",
            field=models.BigIntegerField(
                blank=True,
                help_text="Visit 50000 PokéStops.",
                null=True,
                verbose_name="Backpacker",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_raid_battle_won",
            field=models.BigIntegerField(
                blank=True, help_text="Win 2000 raids.", null=True, verbose_name="Champion"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_raids_with_friends",
            field=models.BigIntegerField(
                blank=True,
                help_text="Win 2000 raids with a friend.",
                null=True,
                verbose_name="Rising Star Duo",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_rocket_giovanni_defeated",
            field=models.BigIntegerField(
                blank=True,
                help_text="Defeat the Team GO Rocket Boss 50 times. ",
                null=True,
                verbose_name="Ultra Hero",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_rocket_grunts_defeated",
            field=models.BigIntegerField(
                blank=True,
                help_text="Defeat 2000 Team GO Rocket Grunts.",
                null=True,
                verbose_name="Hero",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_small_rattata",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 1000 tiny Rattata.",
                null=True,
                verbose_name="Youngster",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_total_mega_evos",
            field=models.BigIntegerField(
                blank=True,
                help_text="Mega Evolve a Pokémon 1000 times.",
                null=True,
                verbose_name="Successor",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_trading",
            field=models.BigIntegerField(
                blank=True, help_text="Trade 2500 Pokémon.", null=True, verbose_name="Gentleman"
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_trading_distance",
            field=models.BigIntegerField(
                blank=True,
                help_text="Earn 10000000 km across the distance of all Pokémon trades.",
                null=True,
                verbose_name="Pilot",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_bug",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Bug-type Pokémon.",
                null=True,
                verbose_name="Bug Catcher",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_dark",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Dark-type Pokémon.",
                null=True,
                verbose_name="Delinquent",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_dragon",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Dragon-type Pokémon.",
                null=True,
                verbose_name="Dragon Tamer",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_electric",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Electric-type Pokémon.",
                null=True,
                verbose_name="Rocker",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_fairy",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Fairy-type Pokémon.",
                null=True,
                verbose_name="Fairy Tale Girl",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_fighting",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Fighting-type Pokémon.",
                null=True,
                verbose_name="Black Belt",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_fire",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Fire-type Pokémon.",
                null=True,
                verbose_name="Kindler",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_flying",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Flying-type Pokémon.",
                null=True,
                verbose_name="Bird Keeper",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_ghost",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Ghost-type Pokémon.",
                null=True,
                verbose_name="Hex Maniac",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_grass",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Grass-type Pokémon.",
                null=True,
                verbose_name="Gardener",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_ground",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Ground-type Pokémon.",
                null=True,
                verbose_name="Ruin Maniac",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_ice",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Ice-type Pokémon.",
                null=True,
                verbose_name="Skier",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_normal",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Normal-type Pokémon.",
                null=True,
                verbose_name="Schoolkid",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_poison",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Poison-type Pokémon.",
                null=True,
                verbose_name="Punk Girl",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_psychic",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Psychic-type Pokémon.",
                null=True,
                verbose_name="Psychic",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_rock",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Rock-type Pokémon.",
                null=True,
                verbose_name="Hiker",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_steel",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Steel-type Pokémon.",
                null=True,
                verbose_name="Rail Staff",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_type_water",
            field=models.BigIntegerField(
                blank=True,
                help_text="Catch 200 Water-type Pokémon.",
                null=True,
                verbose_name="Swimmer",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_ultra_league",
            field=models.BigIntegerField(
                blank=True,
                help_text="Win 1000 Trainer Battles in the Ultra League.",
                null=True,
                verbose_name="Ultra League Veteran",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_unique_pokestops",
            field=models.BigIntegerField(
                blank=True,
                help_text="Visit 2000 unique PokéStops.",
                null=True,
                verbose_name="Sightseer",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_wayfarer",
            field=models.BigIntegerField(
                blank=True,
                help_text="Earn 1500 Wayfarer Agreements",
                null=True,
                verbose_name="Wayfarer",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="battle_hub_stats_battles",
            field=models.BigIntegerField(
                blank=True,
                help_text="You can find this by clicking the Battle button in your game.",
                null=True,
                verbose_name="Battles",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="battle_hub_stats_stardust",
            field=models.BigIntegerField(
                blank=True,
                help_text="You can find this by clicking the Battle button in your game.",
                null=True,
                verbose_name="Stardust Earned",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="battle_hub_stats_wins",
            field=models.BigIntegerField(
                blank=True,
                help_text="You can find this by clicking the Battle button in your game.",
                null=True,
                verbose_name="Wins",
            ),
        ),
        migrations.AlterField(
            model_name="update",
            name="total_xp",
            field=models.BigIntegerField(blank=True, null=True, verbose_name="Total XP"),
        ),
    ]
