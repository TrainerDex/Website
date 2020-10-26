from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework import pagination
from rest_framework.response import Response


class LeaderboardPagination(pagination.LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        dflt = super().paginate_queryset(queryset, request, view)
        self.get_aggregations(queryset)
        return dflt

    def get_aggregations(self, queryset, value="value"):
        try:
            aggr = queryset.aggregate(
                avg=Avg(value),
                count=Count(value),
                min=Min(value),
                max=Max(value),
                sum=Sum(value),
            )
        except (AttributeError, TypeError):
            self.avg = None
            self.count = self.get_count(queryset)
            self.min = None
            self.max = None
            self.sum = None
        else:
            self.avg = aggr.get("avg")
            self.count = aggr.get("count")
            self.min = aggr.get("min")
            self.max = aggr.get("max")
            self.sum = aggr.get("sum")

    def get_paginated_response(self, data, **kwargs):
        data = {
            "avg": self.avg,
            "count": self.count,
            "min": self.min,
            "max": self.max,
            "sum": self.sum,
            "links": {"next": self.get_next_link(), "previous": self.get_previous_link()},
            "results": data,
        }
        return Response({**kwargs, **data})
