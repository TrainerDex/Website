from rest_framework import serializers

from core.models.main import ServiceStatus


class ServiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStatus
        fields = ["uuid", "status", "created_at", "reason"]


class ListServiceSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        serializer = ServiceStatusSerializer(obj.statuses_ordered[0], many=False)
        return serializer.data


class DetailServiceSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    status = serializers.SerializerMethodField()

    def get_statuses(self, obj):
        serializer = ServiceStatusSerializer(obj.statuses_ordered, many=True)
        return serializer.data
