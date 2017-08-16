from django.shortcuts import render
from config.es_client import es_client
from .search_indexes import Gym
from rest_framework_elasticsearch import es_views, es_pagination, es_filters

class GymView(es_views.ListElasticAPIView):
    es_client = es_client
    es_model = Gym
    es_paginator = es_pagination.ElasticLimitOffsetPagination()

# Create your views here.
