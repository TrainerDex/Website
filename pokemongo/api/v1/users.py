import logging

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from allauth.socialaccount.models import SocialAccount

from pokemongo.api.v1.serializers import UserSerializer, SocialAllAuthSerializer

logger = logging.getLogger("django.trainerdex")
User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.exclude(is_active=False)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class SocialLookupView(APIView):
    """
    get:
        kwargs:
            provider (requiered) - platform, options are 'facebook', 'twitter', 'discord', 'google', 'patreon'

            uid - Social ID, supports a comma seperated list. Could be useful for passing a list of users in a server to retrieve a list of UserIDs, which could then be passed to api/v1/leaderboard/
            user - TrainerDex User ID, supports a comma seperated list
            trainer - TrainerDex Trainer ID

    patch:
    Register a SocialAccount. Patch if exists, post if not.
    """

    def get(self, request: HttpRequest) -> Response:
        query = SocialAccount.objects.exclude(user__is_active=False).filter(
            provider=request.GET.get("provider")
        )
        if request.GET.get("uid"):
            query = query.filter(uid__in=request.GET.get("uid").split(","))
        elif request.GET.get("user"):
            query = query.filter(user__in=request.GET.get("user").split(","))
        elif request.GET.get("trainer"):
            query = query.filter(user__trainer=request.GET.get("trainer"))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SocialAllAuthSerializer(query, many=True)
        return Response(serializer.data)

    def put(self, request: HttpRequest) -> Response:
        try:
            query = SocialAccount.objects.exclude(user__is_active=False).get(
                provider=request.data["provider"], uid=request.data["uid"]
            )
        except:
            serializer = SocialAllAuthSerializer(data=request.data)
        else:
            serializer = SocialAllAuthSerializer(query, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
