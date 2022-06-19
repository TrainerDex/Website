from rest_framework import serializers


class TrainerDetailSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
