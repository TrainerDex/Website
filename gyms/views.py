from django.shortcuts import render
from config.es_client import es_client
from gyms.search_indexes import GymIndex
from rest_framework_elasticsearch import es_views, es_pagination, es_filters

class RaidActiveFilter(object):
    def filter_search(self, request, search, view):
        if request.query_params.get('raid_active', None):
            search = search.filter('range', raid_start={'lte': 'now'})
            search = search.filter('range', raid_end={'gte': 'now'})
        return search

class GymView(es_views.ListElasticAPIView):
    es_client = es_client
    es_model = GymIndex
    es_paginator = es_pagination.ElasticLimitOffsetPagination()
    es_filter_backends = (
        es_filters.ElasticFieldsFilter,
        es_filters.ElasticSearchFilter,
        es_filters.ElasticOrderingFilter,
        RaidActiveFilter,
    )
    es_ordering = '-raid_level'
    es_filter_fields = ()
    es_search_fields = (
        'title',
    )
