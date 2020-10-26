import logging
from datetime import datetime, timedelta

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import authentication, status
from rest_framework.views import APIView
from rest_framework.response import Response

from pokemongo.models import Trainer, Update
from pokemongo.api.v1.serializers import (
    DetailedTrainerSerializer,
    BriefUpdateSerializer,
    DetailedUpdateSerializer,
)

logger = logging.getLogger("django.trainerdex")


def recent(value: datetime) -> bool:
    if timezone.now() - timedelta(hours=1) <= value <= timezone.now():
        return True
    return False


class TrainerListView(APIView):
    """
    get:
    Accepts paramaters for Team (t) and Nickname (q)

    post:
    Register a Trainer, needs the Primary Key of the Owner, the User object which owns the Trainer
    """

    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request: HttpRequest) -> Response:
        queryset = Trainer.objects.exclude(owner__is_active=False)
        if not request.user.is_superuser:
            queryset = queryset.exclude(statistics=False)
        if request.GET.get("q") or request.GET.get("t"):
            if request.GET.get("q"):
                queryset = queryset.filter(nickname__nickname__iexact=request.GET.get("q"))
            if request.GET.get("t"):
                queryset = queryset.filter(faction=request.GET.get("t"))

        serializer = DetailedTrainerSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request: HttpRequest) -> Response:
        """
        This used to work as a simple post, but since the beginning of transitioning to API v2 it would have always given Validation Errors if left the same.
        Now it has a 60 minute open slot to work after the auth.User (owner) instance is created. After which, a PATCH request must be given. This is due to the nature of a Trainer being created automatically for all new auth.User
        """

        trainer = Trainer.objects.get(owner__pk=request.data["owner"], owner__is_active=True)
        if not recent(trainer.owner.date_joined):
            return Response(
                {
                    "_error": "profile already exists, please use patch on trainer uri instead or check the owner pk is correct",
                    "_profile_id": trainer.pk,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = DetailedTrainerSerializer(trainer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainerDetailView(APIView):
    """
    get:
    Trainer detail

    patch:
    Update a trainer

    delete:
    Archives a trainer
    """

    authentication_classes = (authentication.TokenAuthentication,)

    def get_object(self, pk: int) -> Trainer:
        return get_object_or_404(Trainer, pk=pk, owner__is_active=True)

    def get(self, request: HttpRequest, pk: int) -> Response:
        trainer = self.get_object(pk)
        if trainer.active is True and (
            trainer.statistics is True or request.user.is_superuser is True
        ):
            serializer = DetailedTrainerSerializer(trainer)
            return Response(serializer.data)
        elif (trainer.active is False) or (trainer.statistics is False):
            response = {
                "code": 1,
                "reason": "Profile deactivated",
                "profile": {"id": trainer.pk},
            }
            return Response(response, status=status.HTTP_423_LOCKED)
        return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request: HttpRequest, pk: int) -> Response:
        trainer = self.get_object(pk)
        serializer = DetailedTrainerSerializer(trainer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: HttpRequest, pk: int) -> Response:
        trainer = self.get_object(pk)
        if trainer.active:
            trainer.active = False
            trainer.save()
            response = {
                "code": 1,
                "reason": "Profile deactivated",
                "profile": {"id": trainer.pk, "faction": trainer.faction},
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateListView(APIView):
    """
    get:
    Takes Trainer ID as part of URL, optional param: detail, shows all detail, otherwise, returns a list of objects with fields 'time_updated' (datetime), 'xp'(int) and 'fields_updated' (list)

    post:
    Create a update
    """

    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request: HttpRequest, pk: int) -> Response:
        updates = Update.objects.filter(trainer=pk, trainer__owner__is_active=True)
        serializer = (
            BriefUpdateSerializer(updates, many=True)
            if request.GET.get("detail") != "1"
            else DetailedUpdateSerializer(updates, many=True)
        )
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def post(self, request: HttpRequest, pk: int) -> Response:
        serializer = DetailedUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(trainer=get_object_or_404(Trainer, pk=pk, owner__is_active=True))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.post(self, request, pk)


class LatestUpdateView(APIView):
    """
    get:
    Gets detailed view of the latest update

    patch:
    Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked.
    """

    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request: HttpRequest, pk: int) -> Response:
        try:
            update = Update.objects.filter(trainer=pk, trainer__owner__is_active=True).latest(
                "update_time"
            )
        except Update.DoesNotExist:
            return Response(None, status=404)
        serializer = DetailedUpdateSerializer(update)
        return Response(serializer.data)

    def patch(self, request: HttpRequest, pk: int) -> Response:
        update = Update.objects.filter(trainer=pk, trainer__owner__is_active=True).latest(
            "update_time"
        )
        if update.meta_time_created > timezone.now() - timedelta(minutes=32):
            serializer = DetailedUpdateSerializer(update, data=request.data)
            if serializer.is_valid():
                serializer.clean()
                serializer.save(trainer=update.trainer, uuid=update.uuid, pk=update.pk)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDetailView(APIView):
    """
    get:
    Gets detailed view

    patch:
    Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked"""

    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request: HttpRequest, uuid: str, pk: int) -> Response:
        update = get_object_or_404(Update, trainer=pk, uuid=uuid, trainer__owner__is_active=True)
        serializer = DetailedUpdateSerializer(update)
        if update.trainer.id != int(pk):
            return Response(status=400)
        return Response(serializer.data)

    def patch(self, request: HttpRequest, uuid: str, pk: int) -> Response:
        update = get_object_or_404(Update, trainer=pk, uuid=uuid, trainer__owner__is_active=True)
        if update.meta_time_created > timezone.now() - timedelta(minutes=32):
            serializer = DetailedUpdateSerializer(update, data=request.data)
            if serializer.is_valid():
                serializer.clean()
                serializer.save(trainer=update.trainer, uuid=update.uuid, pk=update.pk)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
