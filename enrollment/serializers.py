from rest_framework import serializers
from enrollment.models import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'


class CreateEnrollmentSerializer(serializers.ModelSerializer):
    discord_ids = serializers.ListField(serializers.IntegerField)
    class Meta:
        model = Enrollment
        fields = '__all__'


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
