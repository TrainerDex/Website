from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers

from pokemongo.models import Nickname, Update
from pokemongo.shortcuts import BATTLE_HUB_STATS, STANDARD_MEDALS, UPDATE_FIELDS_TYPES


class TrainerDetailSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    nickname = serializers.CharField(source="_nickname")
    start_date = serializers.DateField()
    faction = serializers.IntegerField()
    trainer_code = serializers.CharField()

    # Any below this point may be removed before release.

    verified = serializers.BooleanField()
    statistics = serializers.BooleanField()
    has_cheated = serializers.BooleanField()
    last_cheated = serializers.DateField()
    currently_banned = serializers.BooleanField()


class NicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nickname
        fields = ("nickname", "active")


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ("provider", "uid")


class UpdateSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        optional_fields = (x.name for x in Update._meta.fields if x.null)
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
                "created_at",
                "updated_at",
                "update_time",
                "total_xp",
                "pokedex_caught",
                "pokedex_seen",
                "gym_gold",
            ]
            + STANDARD_MEDALS
            + BATTLE_HUB_STATS
            + UPDATE_FIELDS_TYPES
            + ["data_source"]
        )
