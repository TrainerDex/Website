from rest_framework_elasticsearch.es_serializer import ElasticModelSerializer
from gyms.models import Gym
from gyms.search_indexes import GymIndex
from rest_framework import serializers
from django.utils import timezone

class ElasticGymSerializer(ElasticModelSerializer):
    class Meta:
        model = Gym
        es_model = GymIndex
        fields = '__all__'
