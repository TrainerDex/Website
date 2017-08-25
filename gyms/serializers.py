from rest_framework_elasticsearch.es_serializer import ElasticModelSerializer
from .models import Gym
from .search_indexes import GymIndex
from rest_framework import serializers
from django.utils import timezone

class ElasticGymSerializer(ElasticModelSerializer):
    class Meta:
        model = Gym
        es_model = GymIndex
        fields = '__all__'
