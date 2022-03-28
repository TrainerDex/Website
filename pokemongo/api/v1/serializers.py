from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Mapping, TypeVar

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework import serializers

from pokemongo.models import Faction, Trainer, Update
from pokemongo.shortcuts import UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class BriefUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.IntegerField(source="total_xp", read_only=True)

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


_ValidatedData = TypeVar("_ValidatedData", bound=Mapping)


class DetailedUpdateSerializer(serializers.ModelSerializer):
    xp = serializers.IntegerField(source="total_xp", read_only=True)

    def validate(self, attrs: _ValidatedData) -> _ValidatedData:
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
            [
                "uuid",
                "trainer",
                "update_time",
                "xp",
                "total_xp",
                "pokedex_caught",
                "pokedex_seen",
                "gymbadges_gold",
            ]
            + UPDATE_FIELDS_BADGES
            + UPDATE_FIELDS_TYPES
            + ["data_source"]
        )


class DetailedTrainerSerializer(serializers.ModelSerializer):
    update_set = BriefUpdateSerializer(read_only=True, many=True)
    prefered = serializers.BooleanField(default=True, read_only=True)
    username = serializers.CharField(source="nickname", read_only=True)
    last_modified = serializers.DateTimeField(source="updated_at", read_only=True)

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
    def create(self, validated_data: Mapping) -> User:
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "profiles", "trainer")
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
    level = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    faction = serializers.SerializerMethodField()
    xp = serializers.SerializerMethodField()
    total_xp = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_position(self, obj: Update) -> int:
        return obj.rank

    def get_level(self, obj: Update) -> str:
        return str(obj.level())

    def get_id(self, obj: Update) -> int:
        return obj.trainer.id

    def get_username(self, obj: Update) -> str:
        try:
            return [x.nickname for x in obj.trainer.nickname_set.all() if x.active][0]
        except IndexError:
            return "Unknown"

    def get_faction(self, obj: Update) -> dict[str, str | int]:
        return FactionSerializer(obj.trainer.faction).data

    def get_xp(self, obj: Update) -> int:
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp

    def get_total_xp(self, obj: Update) -> int:
        """This field is deprecated and will be removed in API v2"""
        return obj.total_xp

    def get_value(self, obj: Update) -> int:
        return obj.value

    def get_last_updated(self, obj: Update) -> datetime.datetime:
        return obj.update_time

    def get_user_id(self, obj: Update) -> int:
        return obj.trainer.owner.pk

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
