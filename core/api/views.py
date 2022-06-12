from __future__ import annotations

from uuid import UUID

from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from core.api.decorators import required_scopes
from core.api.serializers import ListServiceSerializer
from core.models.main import Service, ServiceStatus


class ServiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        queryset: QuerySet[Service] = Service.objects.prefetch_related(
            Prefetch(
                "statuses",
                ServiceStatus.objects.order_by("-created_at"),
                to_attr="statuses_ordered",
            )
        )
        serializer = ListServiceSerializer(queryset, many=True)
        return Response(serializer.data)


class ServiceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, uuid: UUID) -> Response:
        queryset: QuerySet[Service] = Service.objects.prefetch_related(
            Prefetch(
                "statuses",
                ServiceStatus.objects.order_by("-created_at"),
                to_attr="statuses_ordered",
            )
        )
        service: Service = get_object_or_404(queryset, uuid=uuid)
        serializer = ListServiceSerializer(service)
        return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request: Request) -> Response:
    return Response(status=HTTP_204_NO_CONTENT)


@api_view(["GET"])
@authentication_classes([OAuth2Authentication])
@permission_classes([TokenHasScope])
@required_scopes(["read"])
def test_oauth(request: Request) -> Response:
    return Response(status=HTTP_204_NO_CONTENT)
