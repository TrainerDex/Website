import datetime
from typing import Dict, List, Optional, Union

from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers
from django.contrib.auth import get_user_model
from pokemongo.models import Update, Trainer, Faction
from pokemongo.shortcuts import level_parser, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES

User = get_user_model()


class BriefUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.SerializerMethodField()

    def get_xp(self, obj: Update) -> int:
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp

    class Meta:
        model = Update
        fields = [
            "uuid",
            "trainer",
            "update_time",
            "xp",
            "total_xp",
            "modified_extra_fields",
        ]


class DetailedUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.SerializerMethodField()

    def get_xp(self, obj: Update) -> int:
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp

    def validate(self, attrs: Dict) -> Dict:
        """This method takes a single argument, which is a dictionary of field values.

        It should raise a :serializers.ValidationError: if necessary,
        or just return the validated values.
        """
        instance = Update(**attrs)
        instance.clean()
        return attrs

    class Meta:
        model = Update
        fields = (
            (
                "uuid",
                "trainer",
                "update_time",
                "xp",
                "total_xp",
                "pokedex_caught",
                "pokedex_seen",
                "gymbadges_total",
                "gymbadges_gold",
                "pokemon_info_stardust",
            )
            + UPDATE_FIELDS_BADGES
            + UPDATE_FIELDS_TYPES
            + ("data_source",)
        )


class DetailedTrainerSerializer(serializers.ModelSerializer):
    update_set = BriefUpdateSerializer(read_only=True, many=True)
    prefered = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_prefered(self, obj: Trainer) -> bool:
        """This field is deprecated and will be removed in API v2"""
        return True

    def get_username(self, obj: Trainer) -> str:
        return obj.nickname

    class Meta:
        model = Trainer
        fields = (
            "id",
            "last_modified",
            "owner",
            "username",
            "start_date",
            "faction",
            "trainer_code",
            "has_cheated",
            "last_cheated",
            "currently_cheats",
            "daily_goal",
            "total_goal",
            "update_set",
            "prefered",
            "verified",
            "statistics",
        )


class UserSerializer(serializers.ModelSerializer):
    profiles = serializers.SerializerMethodField()

    def get_profiles(self, obj: User) -> List[int]:
        """This field is deprecated and will be removed in API v2"""
        try:
            return [obj.trainer.pk]
        except User.trainer.RelatedObjectDoesNotExist:
            return []

    def create(self, validated_data: Dict) -> User:
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "profiles", "trainer")
        read_only_fields = ("profiles", "trainer")


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
    level = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    faction = serializers.SerializerMethodField()
    xp = serializers.SerializerMethodField()
    total_xp = serializers.SerializerMethodField()
    stat = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_position(self, obj: Update) -> int:
        return obj.rank

    def get_level(self, obj: Update) -> Optional[int]:
        try:
            return level_parser(xp=obj.total_xp).level
        except ValueError:
            return None

    def get_id(self, obj: Update) -> int:
        return obj.trainer.id

    def get_username(self, obj: Update) -> str:
        return obj.trainer.nickname

    def get_faction(self, obj: Update) -> Dict[str, Union[str, int]]:
        return FactionSerializer(obj.trainer.faction).data

    def get_xp(self, obj: Update) -> int:
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp

    def get_total_xp(self, obj: Update) -> int:
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp

    def get_stat(self, obj: Update) -> int:
        return obj.value

    def get_last_updated(self, obj: Update) -> datetime.datetime:
        return obj.datetime

    def get_user_id(self, obj: Update) -> Optional[int]:
        return obj.trainer.owner.pk if obj.trainer.owner else None

    class Meta:
        model = Update
        fields = (
            "position",
            "id",
            "username",
            "faction",
            "level",
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
