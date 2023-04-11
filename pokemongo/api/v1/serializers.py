from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, TypeVar

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework import serializers

from pokemongo.models import BATTLE_HUB_STATS, STANDARD_MEDALS, UPDATE_FIELDS_TYPES, Faction, Trainer, Update

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

_ValidatedData = TypeVar("_ValidatedData", bound=Mapping)


class BriefUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.IntegerField(
        source="total_xp",
        read_only=True,
    )

    class Meta:
        model = Update
        fields = [
            "uuid",
            "trainer",
            "update_time",
            "xp",
            "trainer_level",
            "total_xp",
            "modified_extra_fields",
        ]


class DetailedUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.IntegerField(
        source="total_xp",
        read_only=True,
    )
    gymbadges_gold = serializers.IntegerField(
        source="gym_gold",
        read_only=True,
    )
    badge_travel_km = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
        source="travel_km",
        read_only=True,
    )
    badge_pokedex_entries = serializers.IntegerField(
        source="pokedex_entries",
        read_only=True,
    )
    badge_capture_total = serializers.IntegerField(
        source="capture_total",
        read_only=True,
    )
    badge_evolved_total = serializers.IntegerField(
        source="evolved_total",
        read_only=True,
    )
    badge_hatched_total = serializers.IntegerField(
        source="hatched_total",
        read_only=True,
    )
    badge_pokestops_visited = serializers.IntegerField(
        source="pokestops_visited",
        read_only=True,
    )
    badge_unique_pokestops = serializers.IntegerField(
        source="unique_pokestops",
        read_only=True,
    )
    badge_big_magikarp = serializers.IntegerField(
        source="big_magikarp",
        read_only=True,
    )
    badge_battle_attack_won = serializers.IntegerField(
        source="battle_attack_won",
        read_only=True,
    )
    badge_battle_training_won = serializers.IntegerField(
        source="battle_training_won",
        read_only=True,
    )
    badge_small_rattata = serializers.IntegerField(
        source="small_rattata",
        read_only=True,
    )
    badge_pikachu = serializers.IntegerField(
        source="pikachu",
        read_only=True,
    )
    badge_unown = serializers.IntegerField(
        source="unown",
        read_only=True,
    )
    badge_pokedex_entries_gen2 = serializers.IntegerField(
        source="pokedex_entries_gen2",
        read_only=True,
    )
    badge_raid_battle_won = serializers.IntegerField(
        source="raid_battle_won",
        read_only=True,
    )
    badge_legendary_battle_won = serializers.IntegerField(
        source="legendary_battle_won",
        read_only=True,
    )
    badge_berries_fed = serializers.IntegerField(
        source="berries_fed",
        read_only=True,
    )
    badge_hours_defended = serializers.IntegerField(
        source="hours_defended",
        read_only=True,
    )
    badge_pokedex_entries_gen3 = serializers.IntegerField(
        source="pokedex_entries_gen3",
        read_only=True,
    )
    badge_challenge_quests = serializers.IntegerField(
        source="challenge_quests",
        read_only=True,
    )
    badge_max_level_friends = serializers.IntegerField(
        source="max_level_friends",
        read_only=True,
    )
    badge_trading = serializers.IntegerField(
        source="trading",
        read_only=True,
    )
    badge_trading_distance = serializers.IntegerField(
        source="trading_distance",
        read_only=True,
    )
    badge_pokedex_entries_gen4 = serializers.IntegerField(
        source="pokedex_entries_gen4",
        read_only=True,
    )
    badge_great_league = serializers.IntegerField(
        source="great_league",
        read_only=True,
    )
    badge_ultra_league = serializers.IntegerField(
        source="ultra_league",
        read_only=True,
    )
    badge_master_league = serializers.IntegerField(
        source="master_league",
        read_only=True,
    )
    badge_photobomb = serializers.IntegerField(
        source="photobomb",
        read_only=True,
    )
    badge_pokedex_entries_gen5 = serializers.IntegerField(
        source="pokedex_entries_gen5",
        read_only=True,
    )
    badge_pokemon_purified = serializers.IntegerField(
        source="pokemon_purified",
        read_only=True,
    )
    badge_rocket_grunts_defeated = serializers.IntegerField(
        source="rocket_grunts_defeated",
        read_only=True,
    )
    badge_rocket_giovanni_defeated = serializers.IntegerField(
        source="rocket_giovanni_defeated",
        read_only=True,
    )
    badge_buddy_best = serializers.IntegerField(
        source="buddy_best",
        read_only=True,
    )
    badge_pokedex_entries_gen6 = serializers.IntegerField(
        source="pokedex_entries_gen6",
        read_only=True,
    )
    badge_pokedex_entries_gen7 = serializers.IntegerField(
        source="pokedex_entries_gen7",
        read_only=True,
    )
    badge_pokedex_entries_gen8 = serializers.IntegerField(
        source="pokedex_entries_gen8",
        read_only=True,
    )
    badge_seven_day_streaks = serializers.IntegerField(
        source="seven_day_streaks",
        read_only=True,
    )
    badge_unique_raid_bosses_defeated = serializers.IntegerField(
        source="unique_raid_bosses_defeated",
        read_only=True,
    )
    badge_raids_with_friends = serializers.IntegerField(
        source="raids_with_friends",
        read_only=True,
    )
    badge_pokemon_caught_at_your_lures = serializers.IntegerField(
        source="pokemon_caught_at_your_lures",
        read_only=True,
    )
    badge_wayfarer = serializers.IntegerField(
        source="wayfarer",
        read_only=True,
    )
    badge_total_mega_evos = serializers.IntegerField(
        source="total_mega_evos",
        read_only=True,
    )
    badge_unique_mega_evos = serializers.IntegerField(
        source="unique_mega_evos",
        read_only=True,
    )
    badge_trainers_referred = serializers.IntegerField(
        source="trainers_referred",
        read_only=True,
    )
    badge_mvt = serializers.IntegerField(
        source="mvt",
        read_only=True,
    )
    badge_type_normal = serializers.IntegerField(
        source="type_normal",
        read_only=True,
    )
    badge_type_fighting = serializers.IntegerField(
        source="type_fighting",
        read_only=True,
    )
    badge_type_flying = serializers.IntegerField(
        source="type_flying",
        read_only=True,
    )
    badge_type_poison = serializers.IntegerField(
        source="type_poison",
        read_only=True,
    )
    badge_type_ground = serializers.IntegerField(
        source="type_ground",
        read_only=True,
    )
    badge_type_rock = serializers.IntegerField(
        source="type_rock",
        read_only=True,
    )
    badge_type_bug = serializers.IntegerField(
        source="type_bug",
        read_only=True,
    )
    badge_type_ghost = serializers.IntegerField(
        source="type_ghost",
        read_only=True,
    )
    badge_type_steel = serializers.IntegerField(
        source="type_steel",
        read_only=True,
    )
    badge_type_fire = serializers.IntegerField(
        source="type_fire",
        read_only=True,
    )
    badge_type_water = serializers.IntegerField(
        source="type_water",
        read_only=True,
    )
    badge_type_grass = serializers.IntegerField(
        source="type_grass",
        read_only=True,
    )
    badge_type_electric = serializers.IntegerField(
        source="type_electric",
        read_only=True,
    )
    badge_type_psychic = serializers.IntegerField(
        source="type_psychic",
        read_only=True,
    )
    badge_type_ice = serializers.IntegerField(
        source="type_ice",
        read_only=True,
    )
    badge_type_dragon = serializers.IntegerField(
        source="type_dragon",
        read_only=True,
    )
    badge_type_dark = serializers.IntegerField(
        source="type_dark",
        read_only=True,
    )
    badge_type_fairy = serializers.IntegerField(
        source="type_fairy",
        read_only=True,
    )

    def validate(self, attrs: _ValidatedData) -> _ValidatedData:
        """This method takes a single argument, which is a dictionary of field values.

        It should raise a :serializers.ValidationError: if necessary,
        or just return the validated values.
        """
        instance = Update(**attrs)
        instance.clean()
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        optional_fields = (
            [
                "xp",
                "pokedex_caught",
                "pokedex_seen",
                "gymbadges_gold",
                "gym_gold",
            ]
            + [f"badge_{field.name}" for field in STANDARD_MEDALS if field.stat_id < 79]
            + [field.name for field in STANDARD_MEDALS]
            + [field.name for field in BATTLE_HUB_STATS]
            + [f"badge_{field.name}" for field in UPDATE_FIELDS_TYPES]
            + [field.name for field in UPDATE_FIELDS_TYPES]
        )
        for field in optional_fields:
            try:
                if rep[field] is None:
                    rep.pop(field)
            except KeyError:
                pass
        return rep

    class Meta:
        model = Update
        fields = (
            [
                "uuid",
                "trainer",
                "update_time",
                "xp",
                "total_xp",
                "trainer_level",
                "pokedex_caught",
                "pokedex_seen",
                "gymbadges_gold",
                "gym_gold",
            ]
            + [f"badge_{field.name}" for field in STANDARD_MEDALS if field.stat_id < 79]
            + [field.name for field in STANDARD_MEDALS]
            + [field.name for field in BATTLE_HUB_STATS]
            + [f"badge_{field.name}" for field in UPDATE_FIELDS_TYPES]
            + [field.name for field in UPDATE_FIELDS_TYPES]
            + ["data_source"]
        )


class LatestStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = [field.name for field in Update.get_stat_fields()]


class DetailedTrainerSerializer(serializers.ModelSerializer):
    update_set = BriefUpdateSerializer(read_only=True, many=True)
    prefered = serializers.BooleanField(
        default=True,
        read_only=True,
    )
    username = serializers.CharField(
        source="_nickname",
        read_only=True,
    )
    last_modified = serializers.DateTimeField(
        source="updated_at",
        read_only=True,
    )

    class Meta:
        model = Trainer
        fields = (
            "id",
            "uuid",
            "created_at",
            "updated_at",
            "last_modified",
            "owner",
            "username",
            "start_date",
            "faction",
            "trainer_code",
            "has_cheated",
            "last_cheated",
            "currently_banned",
            "daily_goal",
            "total_goal",
            "update_set",
            "prefered",
            "verified",
            "statistics",
        )


class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(source="trainer.uuid", read_only=True)

    def create(self, validated_data: Mapping) -> User:
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ("id", "uuid", "username", "trainer")
        read_only_fields = ("trainer",)


class FactionSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name_en = serializers.SerializerMethodField()

    def get_id(self, obj: Faction) -> int:
        return Faction(obj).id

    def get_name_en(self, obj: Faction) -> str:
        from django.utils import translation

        lang = translation.get_language()
        translation.activate("en")
        result = str(Faction(obj))
        translation.activate(lang)
        return result


class LeaderboardSerializer(serializers.Serializer):
    level = serializers.CharField(
        source="trainer_level",
        read_only=True,
        default="40+",
    )
    position = serializers.IntegerField(
        source="rank",
        read_only=True,
    )
    id = serializers.IntegerField(
        source="trainer.id",
        read_only=True,
    )
    username = serializers.CharField(
        source="trainer._nickname",
        read_only=True,
    )
    faction = FactionSerializer(
        source="trainer.faction",
        read_only=True,
    )
    xp = serializers.IntegerField(
        source="total_xp",
        read_only=True,
    )
    total_xp = serializers.IntegerField(
        read_only=True,
    )
    value = serializers.IntegerField(
        read_only=True,
    )
    last_updated = serializers.DateTimeField(
        source="update_time",
        read_only=True,
    )
    user_id = serializers.IntegerField(
        source="trainer.owner.id",
        read_only=True,
    )

    class Meta:
        model = Update
        fields = (
            "position",
            "id",
            "username",
            "faction",
            "trainer_level",
            "xp",
            "total_xp",
            "stat",
            "last_updated",
            "user_id",
        )


class SocialAllAuthSerializer(serializers.ModelSerializer):
    trainer = serializers.SerializerMethodField()

    def get_trainer(self, obj: SocialAccount) -> int:
        return obj.user.trainer.pk

    class Meta:
        model = SocialAccount
        fields = (
            "user",
            "provider",
            "uid",
            "extra_data",
            "trainer",
        )
