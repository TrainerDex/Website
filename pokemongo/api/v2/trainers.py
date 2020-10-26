import logging

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from pokemongo.models import Update

logger = logging.getLogger("django.trainerdex")


class LatestUpdateRedirector(APIView):
    """
    get:
    Redirects to the Latest Update
    """


    def get(self, request: HttpRequest, pk: int) -> Response:
        try:
            update = Update.objects.filter(trainer=pk, trainer__owner__is_active=True).latest(
                "update_time"
            )
        except Update.DoesNotExist:
            return Response(None, status=404)
        return redirect(reverse("api:trainer-update-detail", kwargs={"pk": pk, "uuid": update.uuid}))
