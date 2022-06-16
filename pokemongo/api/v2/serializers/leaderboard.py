from rest_framework import serializers


class SnapshotLeaderboardAggegrationSerializer(serializers.Serializer):
    average = serializers.DecimalField(decimal_places=2, max_digits=15)
    count = serializers.IntegerField()
    min = serializers.DecimalField(decimal_places=2, max_digits=15)
    max = serializers.DecimalField(decimal_places=2, max_digits=15)
    sum = serializers.DecimalField(decimal_places=2, max_digits=15)


class SnapshotLeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    username = serializers.CharField()
    faction = serializers.IntegerField()
    value = serializers.DecimalField(decimal_places=2, max_digits=15)
    trainer_uuid = serializers.UUIDField()
    entry_uuid = serializers.UUIDField()
    entry_datetime = serializers.DateTimeField()


class SnapshotLeaderboardSerializer(serializers.Serializer):
    """
    Serializer for the SnapshotLeaderboard class.
    """

    generated = serializers.DateTimeField()
    date = serializers.DateField()
    title = serializers.CharField()
    field = serializers.CharField()
    aggregations = SnapshotLeaderboardAggegrationSerializer()
    entries = SnapshotLeaderboardEntrySerializer(many=True)
