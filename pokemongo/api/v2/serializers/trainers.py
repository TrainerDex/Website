from rest_framework import serializers


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
