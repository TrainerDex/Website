from rest_framework import serializers
from . import models

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollment
        fields = '__all__'


class CreateEnrollmentSerializer(serializers.ModelSerializer):
    discord_ids = serializers.ListField(serializers.IntegerField)
    class Meta:
        model = models.Enrollment
        fields = '__all__'


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollment
        fields = '__all__'
