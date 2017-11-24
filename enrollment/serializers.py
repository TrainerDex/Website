from rest_framework import serializers
from enrollment.models import *

class EnrollmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Enrollment
		fields = '__all__'

class RaidSerializer(serializers.ModelSerializer):
	class Meta:
		model = Raid
		fields = '__all__'
