# Generated by Django 2.1.2 on 2018-11-04 14:07

import colorful.fields
import datetime
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.citext
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import trainer.models
import trainer.validators
import uuid


class Migration(migrations.Migration):

    replaces = [('trainer', '0001_initial'), ('trainer', '0002_auto_20170919_1904'), ('trainer', '0003_auto_20170921_1611'), ('trainer', '0004_auto_20171015_1136'), ('trainer', '0005_auto_20171015_1153'), ('trainer', '0006_update_leg_raids_completed'), ('trainer', '0007_auto_20171107_1943'), ('trainer', '0008_clear_default_start_dates'), ('trainer', '0009_auto_20171209_1502'), ('trainer', '0010_migrate_discord_users'), ('trainer', '0011_rename_servers'), ('trainer', '0012_auto_20171209_1659'), ('trainer', '0013_auto_20171212_2259'), ('trainer', '0014_remove_discord_guild'), ('trainer', '0015_trainer_active'), ('trainer', '0016_update_uuid'), ('trainer', '0017_generate_uuids'), ('trainer', '0018_uuid_unique'), ('trainer', '0019_update_meta_time_created'), ('trainer', '0020_autofll_creation_time'), ('trainer', '0021_auto_20171218_0109'), ('trainer', '0022_auto_20171219_1654'), ('trainer', '0023_auto_20180102_2130'), ('trainer', '0024_auto_20180103_0029'), ('trainer', '0025_update_meta_source'), ('trainer', '0026_auto_20180104_2329'), ('trainer', '0027_auto_20180105_2237'), ('trainer', '0028_auto_20180105_2330'), ('trainer', '0029_trainerreport'), ('trainer', '0030_auto_20180105_2350'), ('trainer', '0031_auto_20180115_1549'), ('trainer', '0032_auto_20180115_1549'), ('trainer', '0033_auto_20180120_2044'), ('trainer', '0034_auto_20180120_2104'), ('trainer', '0035_auto_20180121_1521'), ('trainer', '0036_auto_20180221_2015'), ('trainer', '0037_trainer_event_10b'), ('trainer', '0038_auto_20180222_2221'), ('trainer', '0039_auto_20180301_0954'), ('trainer', '0040_auto_20180312_1957'), ('trainer', '0041_auto_20180315_1112'), ('trainer', '0042_trainer_event_1k_users'), ('trainer', '0043_auto_20180318_1736'), ('trainer', '0044_auto_20180322_1350'), ('trainer', '0045_auto_20180322_1442'), ('trainer', '0046_auto_20180328_1205'), ('trainer', '0047_auto_20180328_1625'), ('trainer', '0048_auto_20180328_1757'), ('trainer', '0049_auto_20180402_1348'), ('trainer', '0050_auto_20180413_1334'), ('trainer', '0051_auto_20180619_2003'), ('trainer', '0052_auto_20180621_1901'), ('trainer', '0053_auto_20180709_1148'), ('trainer', '0054_trainer_trainer_code'), ('trainer', '0055_auto_20180714_1333'), ('trainer', '0056_auto_20180714_1359'), ('trainer', '0057_auto_20180722_1206'), ('trainer', '0058_trainer_special_weekend_2018'), ('trainer', '0059_auto_20180728_1809'), ('trainer', '0060_auto_20180728_1810'), ('trainer', '0061_auto_20180728_1821'), ('trainer', '0062_auto_20180728_1835'), ('trainer', '0063_auto_20180728_1844'), ('trainer', '0064_trainer_thesilphroad_username'), ('trainer', '0065_sponsorship'), ('trainer', '0066_auto_20180730_1147'), ('trainer', '0067_auto_20180804_1141'), ('trainer', '0068_auto_20180809_1808'), ('trainer', '0069_auto_20180810_1820'), ('trainer', '0070_auto_20180809_1829'), ('trainer', '0071_auto_20180810_2217'), ('trainer', '0072_auto_20180813_0121'), ('trainer', '0073_auto_20180815_1323'), ('trainer', '0074_auto_20180817_1121'), ('trainer', '0075_auto_20180819_1400'), ('trainer', '0076_auto_20180820_1434'), ('trainer', '0077_auto_20180824_1543'), ('trainer', '0078_update_gen_4_dex'), ('trainer', '0079_rename_fields'), ('trainer', '0080_auto_20181017_1043')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.CITIES_COUNTRY_MODEL),
        ('cities', '0011_auto_20180108_0706'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityLeague',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='UUID')),
                ('language', models.CharField(choices=[('en', 'English'), ('de', 'German'), ('es', 'Spanish'), ('fr', 'French'), ('it', 'Italian'), ('ja', 'Japanese'), ('ko', 'Korean'), ('pt-br', 'Brazilian Portuguese'), ('zh-hant', 'Traditional Chinese')], max_length=7)),
                ('short_description', models.CharField(max_length=70)),
                ('description', models.TextField(blank=True, null=True)),
                ('vanity', models.SlugField()),
                ('privacy_public', models.BooleanField(default=False)),
                ('security_ban_sync', models.BooleanField(default=False)),
                ('security_kick_sync', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Community League',
                'verbose_name_plural': 'Community Leagues',
            },
        ),
        migrations.CreateModel(
            name='CommunityLeagueMembershipDiscord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_import', models.BooleanField(default=True)),
                ('security_ban_sync', models.NullBooleanField()),
                ('security_kick_sync', models.NullBooleanField()),
            ],
            options={
                'verbose_name': 'Community League Discord Connection',
                'verbose_name_plural': 'Community League Discord Connections',
            },
        ),
        migrations.CreateModel(
            name='CommunityLeagueMembershipPersonal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary', models.BooleanField(default=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.CommunityLeague')),
            ],
            options={
                'verbose_name': 'Community League Membership',
                'verbose_name_plural': 'Community League Memberships',
            },
        ),
        migrations.CreateModel(
            name='DiscordGuild',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('cached_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('cached_date', models.DateTimeField(auto_now=True)),
                ('setting_channels_ocr_enabled', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), size=None)),
                ('setting_rename_users', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Discord Guild',
                'verbose_name_plural': 'Discord Guilds',
            },
        ),
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name_en', models.CharField(max_length=50, verbose_name='Name (English)')),
                ('name_ja', models.CharField(max_length=50, verbose_name='Name (Japanese)')),
                ('name_fr', models.CharField(max_length=50, verbose_name='Name (French)')),
                ('name_es', models.CharField(max_length=50, verbose_name='Name (Spanish)')),
                ('name_de', models.CharField(max_length=50, verbose_name='Name (German)')),
                ('name_it', models.CharField(max_length=50, verbose_name='Name (Italian)')),
                ('name_ko', models.CharField(max_length=50, verbose_name='Name (Korean)')),
                ('name_zh_Hant', models.CharField(max_length=50, verbose_name='Name (Traditional Chinese)')),
                ('name_pt_BR', models.CharField(max_length=50, verbose_name='Name (Brazilian Portuguese)')),
                ('colour', colorful.fields.RGBColorField(blank=True, default='#929292', null=True, verbose_name='Colour')),
            ],
            options={
                'verbose_name': 'Team',
                'verbose_name_plural': 'Teams',
            },
        ),
        migrations.CreateModel(
            name='Sponsorship',
            fields=[
                ('slug', models.SlugField(primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=20)),
                ('description', models.CharField(db_index=True, max_length=240)),
                ('icon', models.ImageField(upload_to='spon/')),
            ],
            options={
                'verbose_name': 'Special Relationship (Sponsorship)',
                'verbose_name_plural': 'Special Relationships (Sponsorships)',
            },
        ),
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', django.contrib.postgres.fields.citext.CICharField(db_index=True, help_text='Your Trainer Nickname exactly as is in game. You are free to change capitalisation but removal or addition of digits may prevent other Trainers with similar usernames from using this service and is against the Terms of Service.', max_length=15, unique=True, validators=[trainer.validators.PokemonGoUsernameValidator], verbose_name='Nickname')),
                ('start_date', models.DateField(blank=True, help_text='The date you created your Pokémon Go account.', null=True, validators=[django.core.validators.MinValueValidator(datetime.date(2016, 7, 6))], verbose_name='Start Date')),
                ('last_cheated', models.DateField(blank=True, help_text='When did this Trainer last cheat?', null=True, verbose_name='Last Cheated')),
                ('statistics', models.BooleanField(default=True, help_text='Would you like to be shown on the leaderboard? Ticking this box gives us permission to process your data.', verbose_name='Statistics')),
                ('daily_goal', models.PositiveIntegerField(blank=True, help_text="Our Discord bot lets you know if you've reached you goals or not: How much XP do you aim to gain a day?", null=True, verbose_name='Rate Goal')),
                ('total_goal', models.PositiveIntegerField(blank=True, help_text="Our Discord bot lets you know if you've reached you goals or not: How much XP are you aiming for next?", null=True, verbose_name='Reach Goal')),
                ('trainer_code', models.CharField(blank=True, help_text='Fancy sharing your trainer code? (Disclaimer: This information will be public)', max_length=15, null=True, validators=[trainer.validators.TrainerCodeValidator], verbose_name='Trainer Code')),
                ('badge_chicago_fest_july_2017', models.BooleanField(default=False, help_text='Chicago, July 22, 2017', verbose_name='Pokémon GO Fest 2017')),
                ('badge_pikachu_outbreak_yokohama_2017', models.BooleanField(default=False, help_text='Yokohama, August 2017', verbose_name='Pikachu Outbreak 2017')),
                ('badge_safari_zone_europe_2017_09_16', models.BooleanField(default=False, help_text='Europe, September 16, 2017', verbose_name='GO Safari Zone - Europe 2017')),
                ('badge_safari_zone_europe_2017_10_07', models.BooleanField(default=False, help_text='Europe, October 7, 2017', verbose_name='GO Safari Zone - Europe 2017')),
                ('badge_safari_zone_europe_2017_10_14', models.BooleanField(default=False, help_text='Europe, October 14, 2017', verbose_name='GO Safari Zone - Europe 2017')),
                ('badge_chicago_fest_july_2018', models.BooleanField(default=False, help_text='Chicago, July 14-15, 2018', verbose_name='Pokémon GO Fest 2018')),
                ('badge_apac_partner_july_2018_japan', models.BooleanField(default=False, help_text='Japan, July 26-29, 2018', verbose_name='Pokémon GO Special Weekend')),
                ('badge_apac_partner_july_2018_south_korea', models.BooleanField(default=False, help_text='South Korea, July 29, 2018', verbose_name='Pokémon GO Special Weekend')),
                ('badge_yokosuka_29_aug_2018_mikasa', models.BooleanField(default=False, help_text='Yokosuka, Aug 29, 2018-MIKASA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_29_aug_2018_verny', models.BooleanField(default=False, help_text='Yokosuka, Aug 29, 2018-VERNY', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_29_aug_2018_kurihama', models.BooleanField(default=False, help_text='Yokosuka, Aug 29, 2018-KURIHAM', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_30_aug_2018_mikasa', models.BooleanField(default=False, help_text='Yokosuka, Aug 30, 2018-MIKASA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_30_aug_2018_verny', models.BooleanField(default=False, help_text='Yokosuka, Aug 30, 2018-VERNY', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_30_aug_2018_kurihama', models.BooleanField(default=False, help_text='Yokosuka, Aug 30, 2018-KURIHAMA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_31_aug_2018_mikasa', models.BooleanField(default=False, help_text='Yokosuka, Aug 31, 2018-MIKASA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_31_aug_2018_verny', models.BooleanField(default=False, help_text='Yokosuka, Aug 31, 2018-VERNY', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_31_aug_2018_kurihama', models.BooleanField(default=False, help_text='Yokosuka, Aug 31, 2018-KURIHAMA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_1_sep_2018_mikasa', models.BooleanField(default=False, help_text='Yokosuka, Sep 1, 2018-MIKASA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_1_sep_2018_verny', models.BooleanField(default=False, help_text='Yokosuka, Sep 1, 2018-VERNY', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_1_sep_2018_kurihama', models.BooleanField(default=False, help_text='Yokosuka, Sep 1, 2018-KURIHAMA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_2_sep_2018_mikasa', models.BooleanField(default=False, help_text='Yokosuka, Sep 2, 2018-MIKASA', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_2_sep_2018_verny', models.BooleanField(default=False, help_text='Yokosuka, Sep 2, 2018-VERNY', verbose_name='Pokémon GO Safari Zone')),
                ('badge_yokosuka_2_sep_2018_kurihama', models.BooleanField(default=False, help_text='Yokosuka, Sep 2, 2018-KURIHAMA', verbose_name='Pokémon GO Safari Zone')),
                ('verified', models.BooleanField(default=False, verbose_name='Verified')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('event_10b', models.BooleanField(default=False)),
                ('event_1k_users', models.BooleanField(default=False)),
                ('verification', models.ImageField(blank=True, upload_to=trainer.models.VerificationImagePath, verbose_name='Username / Level / Team Screenshot')),
                ('thesilphroad_username', django.contrib.postgres.fields.citext.CICharField(blank=True, help_text='The username you use on The Silph Road, if different from your Trainer Nickname.', max_length=30, null=True, verbose_name='TheSilphRoad Trainer Name')),
            ],
            options={
                'verbose_name': 'Trainer',
                'verbose_name_plural': 'Trainers',
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='TrainerReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report', models.TextField(verbose_name='Report')),
                ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Reported by')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.Trainer', verbose_name='Trainer')),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time Updated')),
                ('submission_date', models.DateTimeField(auto_now_add=True, verbose_name='Submission Datetime')),
                ('data_source', models.CharField(choices=[('?', None), ('cs_social_twitter', 'Twitter (Found)'), ('cs_social_facebook', 'Facebook (Found)'), ('cs_social_youtube', 'YouTube (Found)'), ('cs_?', 'Sourced Elsewhere'), ('ts_social_discord', 'Discord'), ('ts_social_twitter', 'Twitter'), ('ts_direct', 'Directly told (via text)'), ('web_quick', 'Quick Update (Web)'), ('web_detailed', 'Detailed Update (Web)'), ('ts_registration', 'Registration'), ('ss_registration', 'Registration w/ Screenshot'), ('ss_generic', 'Generic Screenshot'), ('ss_ocr', 'OCR Screenshot'), ('com.nianticlabs.pokemongo.friends', 'In Game Friends'), ('com.pokeassistant.trainerstats', 'Poké Assistant'), ('com.pokenavbot.profiles', 'PokeNav'), ('tl40datateam.spreadsheet', 'Tl40 Data Team (Legacy)'), ('com.tl40data.website', 'Tl40 Data Team'), ('com.pkmngots.import', 'Third Saturday')], default='?', max_length=256, verbose_name='Source')),
                ('screenshot', models.ImageField(blank=True, upload_to=trainer.models.VerificationUpdateImagePath, verbose_name='Screenshot')),
                ('double_check_confirmation', models.BooleanField(default=False, help_text='This will silence some errors.', verbose_name='I have double checked this information and it is correct.')),
                ('total_xp', models.PositiveIntegerField(null=True, verbose_name='Total XP')),
                ('pokedex_caught', models.PositiveIntegerField(blank=True, null=True, verbose_name='Unique Species Caught')),
                ('pokedex_seen', models.PositiveIntegerField(blank=True, null=True, verbose_name='Unique Species Seen')),
                ('badge_travel_km', models.DecimalField(blank=True, decimal_places=2, help_text='Walk 1,000 km', max_digits=16, null=True, verbose_name='Jogger')),
                ('badge_pokedex_entries', models.PositiveIntegerField(blank=True, help_text='Register 100 Kanto region Pokémon in the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(151)], verbose_name='Kanto')),
                ('badge_capture_total', models.PositiveIntegerField(blank=True, help_text='Catch 2000 Pokémon.', null=True, verbose_name='Collector')),
                ('badge_evolved_total', models.PositiveIntegerField(blank=True, help_text='Evolve 200 Pokémon.', null=True, verbose_name='Scientist')),
                ('badge_hatched_total', models.PositiveIntegerField(blank=True, help_text='Hatch 500 eggs.', null=True, verbose_name='Breeder')),
                ('badge_pokestops_visited', models.PositiveIntegerField(blank=True, help_text='Visit 2000 PokéStops.', null=True, verbose_name='Backpacker')),
                ('badge_big_magikarp', models.PositiveIntegerField(blank=True, help_text='Catch 300 big Magikarp.', null=True, verbose_name='Fisherman')),
                ('badge_battle_attack_won', models.PositiveIntegerField(blank=True, help_text='Win 1000 Gym battles.', null=True, verbose_name='Battle Girl')),
                ('badge_battle_training_won', models.PositiveIntegerField(blank=True, help_text='Train 1000 times.', null=True, verbose_name='Ace Trainer')),
                ('badge_small_rattata', models.PositiveIntegerField(blank=True, help_text='Catch 300 tiny Rattata.', null=True, verbose_name='Youngster')),
                ('badge_pikachu', models.PositiveIntegerField(blank=True, help_text='Catch 300 Pikachu.', null=True, verbose_name='Pikachu Fan')),
                ('badge_unown', models.PositiveIntegerField(blank=True, help_text='Catch 26 Unown.', null=True, validators=[django.core.validators.MaxValueValidator(28)], verbose_name='Unown')),
                ('badge_pokedex_entries_gen2', models.PositiveIntegerField(blank=True, help_text='Register 70 Pokémon first discovered in the Johto region to the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(99)], verbose_name='Johto')),
                ('badge_raid_battle_won', models.PositiveIntegerField(blank=True, help_text='Win 1000 Raids.', null=True, verbose_name='Champion')),
                ('badge_legendary_battle_won', models.PositiveIntegerField(blank=True, help_text='Win 1000 Legendary Raids.', null=True, verbose_name='Battle Legend')),
                ('badge_berries_fed', models.PositiveIntegerField(blank=True, help_text='Feed 1000 Berries at Gyms.', null=True, verbose_name='Berry Master')),
                ('badge_hours_defended', models.PositiveIntegerField(blank=True, help_text='Defend Gyms for 1000 hours.', null=True, verbose_name='Gym Leader')),
                ('badge_pokedex_entries_gen3', models.PositiveIntegerField(blank=True, help_text='Register 90 Pokémon first discovered in the Hoenn region to the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(126)], verbose_name='Hoenn')),
                ('badge_challenge_quests', models.PositiveIntegerField(blank=True, help_text='Complete 1000 Field Research tasks.', null=True, verbose_name='Pokémon Ranger')),
                ('badge_max_level_friends', models.PositiveIntegerField(blank=True, help_text='Become Best Friends with 3 Trainers.', null=True, validators=[django.core.validators.MaxValueValidator(200)], verbose_name='Idol')),
                ('badge_trading', models.PositiveIntegerField(blank=True, help_text='Trade 1000 Pokémon.', null=True, verbose_name='Gentleman')),
                ('badge_trading_distance', models.PositiveIntegerField(blank=True, help_text='Earn 1000000 km across the distance of all Pokémon trades.', null=True, verbose_name='Pilot')),
                ('badge_pokedex_entries_gen4', models.PositiveIntegerField(blank=True, help_text='Register 80 Pokémon first discovered in the Sinnoh region to the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(107)], verbose_name='Sinnoh')),
                ('badge_type_normal', models.PositiveIntegerField(blank=True, help_text='Catch 200 Normal-type Pokémon', null=True, verbose_name='Schoolkid')),
                ('badge_type_fighting', models.PositiveIntegerField(blank=True, help_text='Catch 200 Fighting-type Pokémon', null=True, verbose_name='Black Belt')),
                ('badge_type_flying', models.PositiveIntegerField(blank=True, help_text='Catch 200 Flying-type Pokémon', null=True, verbose_name='Bird Keeper')),
                ('badge_type_poison', models.PositiveIntegerField(blank=True, help_text='Catch 200 Poison-type Pokémon', null=True, verbose_name='Punk Girl')),
                ('badge_type_ground', models.PositiveIntegerField(blank=True, help_text='Catch 200 Ground-type Pokémon', null=True, verbose_name='Ruin Maniac')),
                ('badge_type_rock', models.PositiveIntegerField(blank=True, help_text='Catch 200 Rock-type Pokémon', null=True, verbose_name='Hiker')),
                ('badge_type_bug', models.PositiveIntegerField(blank=True, help_text='Catch 200 Bug-type Pokémon', null=True, verbose_name='Bug Catcher')),
                ('badge_type_ghost', models.PositiveIntegerField(blank=True, help_text='Catch 200 Ghost-type Pokémon', null=True, verbose_name='Hex Maniac')),
                ('badge_type_steel', models.PositiveIntegerField(blank=True, help_text='Catch 200 Steel-type Pokémon', null=True, verbose_name='Depot Agent')),
                ('badge_type_fire', models.PositiveIntegerField(blank=True, help_text='Catch 200 Fire-type Pokémon', null=True, verbose_name='Kindler')),
                ('badge_type_water', models.PositiveIntegerField(blank=True, help_text='Catch 200 Water-type Pokémon', null=True, verbose_name='Swimmer')),
                ('badge_type_grass', models.PositiveIntegerField(blank=True, help_text='Catch 200 Grass-type Pokémon', null=True, verbose_name='Gardener')),
                ('badge_type_electric', models.PositiveIntegerField(blank=True, help_text='Catch 200 Electric-type Pokémon', null=True, verbose_name='Rocker')),
                ('badge_type_psychic', models.PositiveIntegerField(blank=True, help_text='Catch 200 Pychic-type Pokémon', null=True, verbose_name='Psychic')),
                ('badge_type_ice', models.PositiveIntegerField(blank=True, help_text='Catch 200 Ice-type Pokémon', null=True, verbose_name='Skier')),
                ('badge_type_dragon', models.PositiveIntegerField(blank=True, help_text='Catch 200 Dragon-type Pokémon', null=True, verbose_name='Dragon Tamer')),
                ('badge_type_dark', models.PositiveIntegerField(blank=True, help_text='Catch 200 Dark-type Pokémon', null=True, verbose_name='Delinquent')),
                ('badge_type_fairy', models.PositiveIntegerField(blank=True, help_text='Catch 200 Fairy-type Pokémon', null=True, verbose_name='Fairy Tale Girl')),
                ('gymbadges_total', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1000)], verbose_name='Gym Badges')),
                ('gymbadges_gold', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1000)], verbose_name='Gold Gym Badges')),
                ('pokemon_info_stardust', models.PositiveIntegerField(blank=True, null=True, verbose_name='Stardust')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.Trainer', verbose_name='Trainer')),
            ],
            options={
                'verbose_name': 'Update',
                'verbose_name_plural': 'Updates',
                'ordering': ['-update_time'],
                'get_latest_by': 'update_time',
            },
        ),
        migrations.CreateModel(
            name='FactionLeader',
            fields=[
                ('faction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='leader', serialize=False, to='trainer.Faction', verbose_name='Team')),
                ('name_en', models.CharField(max_length=50, verbose_name='Name (English)')),
                ('name_ja', models.CharField(max_length=50, verbose_name='Name (Japanese)')),
                ('name_fr', models.CharField(max_length=50, verbose_name='Name (French)')),
                ('name_es', models.CharField(max_length=50, verbose_name='Name (Spanish)')),
                ('name_de', models.CharField(max_length=50, verbose_name='Name (German)')),
                ('name_it', models.CharField(max_length=50, verbose_name='Name (Italian)')),
                ('name_ko', models.CharField(max_length=50, verbose_name='Name (Korean)')),
                ('name_zh_Hant', models.CharField(max_length=50, verbose_name='Name (Traditional Chinese)')),
                ('name_pt_BR', models.CharField(max_length=50, verbose_name='Name (Brazilian Portuguese)')),
            ],
            options={
                'verbose_name': 'Team Leader',
                'verbose_name_plural': 'Team Leaders',
            },
        ),
        migrations.AddField(
            model_name='trainer',
            name='faction',
            field=models.ForeignKey(default=0, help_text='Mystic = Blue, Instinct = Yellow, Valor = Red.', on_delete=django.db.models.deletion.SET_DEFAULT, to='trainer.Faction', verbose_name='Team'),
        ),
        migrations.AddField(
            model_name='trainer',
            name='leaderboard_country',
            field=models.ForeignKey(blank=True, help_text='Where are you based?', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leaderboard_trainers_country', to=settings.CITIES_COUNTRY_MODEL, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='trainer',
            name='leaderboard_region',
            field=models.ForeignKey(blank=True, help_text='Where are you based?', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leaderboard_trainers_region', to='cities.Region', verbose_name='Region'),
        ),
        migrations.AddField(
            model_name='trainer',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trainer', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='sponsorship',
            name='members',
            field=models.ManyToManyField(related_name='sponsorships', to='trainer.Trainer'),
        ),
        migrations.AddField(
            model_name='communityleaguemembershippersonal',
            name='trainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.Trainer'),
        ),
        migrations.AddField(
            model_name='communityleaguemembershipdiscord',
            name='discord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.DiscordGuild'),
        ),
        migrations.AddField(
            model_name='communityleaguemembershipdiscord',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.CommunityLeague'),
        ),
        migrations.AddField(
            model_name='communityleague',
            name='memberships_discord',
            field=models.ManyToManyField(through='trainer.CommunityLeagueMembershipDiscord', to='trainer.DiscordGuild'),
        ),
        migrations.AddField(
            model_name='communityleague',
            name='memberships_personal',
            field=models.ManyToManyField(through='trainer.CommunityLeagueMembershipPersonal', to='trainer.Trainer'),
        ),
    ]