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
    stat = serializers.CharField()
    aggregations = SnapshotLeaderboardAggegrationSerializer()
    entries = SnapshotLeaderboardEntrySerializer(many=True)


class GainLeaderboardAggegrationSerializer(serializers.Serializer):
    trainer_count = serializers.IntegerField()
    average_rate = serializers.DecimalField(decimal_places=2, max_digits=15)
    min_rate = serializers.DecimalField(decimal_places=2, max_digits=15)
    max_rate = serializers.DecimalField(decimal_places=2, max_digits=15)
    average_change = serializers.DecimalField(decimal_places=2, max_digits=15)
    min_change = serializers.DecimalField(decimal_places=2, max_digits=15)
    max_change = serializers.DecimalField(decimal_places=2, max_digits=15)
    sum_change = serializers.DecimalField(decimal_places=2, max_digits=15)


class GainLeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    trainer_uuid = serializers.UUIDField(source="uuid")
    username = serializers.CharField(source="_nickname")
    subtrahend_datetime = serializers.DateTimeField()
    subtrahend_value = serializers.DecimalField(decimal_places=2, max_digits=15)
    minuend_datetime = serializers.DateTimeField()
    minuend_value = serializers.DecimalField(decimal_places=2, max_digits=15)
    difference_duration = serializers.DurationField()
    difference_value = serializers.DecimalField(decimal_places=2, max_digits=15)
    difference_value_rate = serializers.DecimalField(decimal_places=2, max_digits=15)
    difference_value_percentage = serializers.DecimalField(decimal_places=2, max_digits=15)


class GainLeaderboardSerializer(serializers.Serializer):
    """
    Serializer for the SnapshotLeaderboard class.
    """

    generated = serializers.DateTimeField()
    subtrahend_date = serializers.DateField()
    minuend_date = serializers.DateField()
    duration = serializers.DurationField()
    title = serializers.CharField()
    stat = serializers.CharField()
    aggregations = SnapshotLeaderboardAggegrationSerializer()
    entries = SnapshotLeaderboardEntrySerializer(many=True)
