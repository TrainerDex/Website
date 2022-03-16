import logging
from datetime import datetime, timedelta
from typing import Dict

import requests
from allauth.socialaccount.models import SocialAccount
from core.models import DiscordGuildSettings, get_guild_info
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, F, Max, Min, Prefetch, Q, Subquery, Sum, Window
from django.db.models.functions import DenseRank
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from pokemongo.api.v1.serializers import (
    DetailedTrainerSerializer,
    DetailedUpdateSerializer,
    LeaderboardSerializer,
    SocialAllAuthSerializer,
    UserSerializer,
)
from pokemongo.models import Community, Nickname, Trainer, Update
from pokemongo.shortcuts import (
    UPDATE_FIELDS_BADGES,
    filter_leaderboard_qs__update,
    get_country_info,
)
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

logger = logging.getLogger("django.trainerdex")
User = get_user_model()


def recent(value: datetime) -> bool:
    if timezone.now() - timedelta(hours=1) <= value <= timezone.now():
        return True
    return False


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.exclude(is_active=False)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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
        serializer = DetailedUpdateSerializer(updates, many=True)
        return Response(serializer.data)

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
    Allows editting of update within 12 hours of creation, after that time, all updates are denied.
    Trainer, UUID and PK are locked.
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
        if update.submission_date > (timezone.now() - timedelta(hours=12)):
            serializer = DetailedUpdateSerializer(update, data=request.data)
            if serializer.is_valid():
                serializer.save(trainer=update.trainer, uuid=update.uuid, pk=update.pk)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "OutOfTime"}, status=status.HTTP_400_BAD_REQUEST)


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
        if update.submission_date > (timezone.now() - timedelta(hours=12)):
            serializer = DetailedUpdateSerializer(update, data=request.data)
            if serializer.is_valid():
                serializer.save(trainer=update.trainer, uuid=update.uuid, pk=update.pk)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


VALID_LB_STATS = UPDATE_FIELDS_BADGES + [
    "pokedex_caught",
    "pokedex_seen",
    "total_xp",
    "gymbadges_gold",
]


class LeaderboardView(APIView):
    """
    Limited to 1000
    """

    def get(
        self,
        request: HttpRequest,
        stat: str = "total_xp",
    ) -> Response:
        if stat not in VALID_LB_STATS:
            return Response(
                {"state": "error", "reason": "invalid stat"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        generated_time = timezone.now()
        query = filter_leaderboard_qs__update(Update.objects)
        if request.GET.get("users"):
            query = filter_leaderboard_qs__update(
                Update.objects.filter(trainer_id__in=request.GET.get("users").split(","))
            )
        leaderboard = (
            Update.objects.filter(
                pk__in=Subquery(
                    query.filter(update_time__lte=generated_time)
                    .annotate(value=F(stat))
                    .exclude(value__isnull=True)
                    .order_by("trainer", "-value")
                    .distinct("trainer")
                    .values("pk")
                )
            )
            .prefetch_related(
                "trainer",
                "trainer__owner",
                Prefetch(
                    "trainer__nickname_set",
                    Nickname.objects.filter(active=True),
                    to_attr="_nickname",
                ),
            )
            .annotate(value=F(stat), datetime=F("update_time"))
            .annotate(rank=Window(expression=DenseRank(), order_by=F("value").desc()))
            .order_by("rank", "-value", "datetime")
        )
        serializer = LeaderboardSerializer(leaderboard[:1000], many=True)
        return Response(serializer.data)


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


class DetailedLeaderboardView(APIView):
    def get(
        self,
        request: HttpRequest,
        stat: int = "total_xp",
        guild: int = None,
        community: str = None,
        country: str = None,
    ) -> Response:
        if stat not in VALID_LB_STATS:
            return Response(
                {"state": "error", "reason": "invalid stat"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        generated_time = timezone.now()

        def get_guild(guild: int) -> DiscordGuildSettings:
            try:
                server = DiscordGuildSettings.objects.get(id=guild)
            except DiscordGuildSettings.DoesNotExist:
                logger.warn(f"Guild with id {guild} not found")
                try:
                    i = get_guild_info(guild)
                except requests.exceptions.HTTPError:
                    return Response(
                        {
                            "error": "Access Denied",
                            "cause": "The bot doesn't have access to this guild.",
                            "solution": "Add the bot account to the guild.",
                            "guild": guild,
                        },
                        status=404,
                    )
                else:
                    logger.info(f"{i['name']} found. Creating.")
                    server = DiscordGuildSettings.objects.create(
                        id=guild, data=i, cached_date=timezone.now()
                    )
                    server.sync_members()

            if not server.data or server.outdated:
                try:
                    server.refresh_from_api()
                except:
                    return Response(status=424)
                else:
                    server.save()

                if not server.has_access:
                    return Response(
                        {
                            "error": "Access Denied",
                            "cause": "The bot doesn't have access to this guild.",
                            "solution": "Add the bot account to the guild.",
                        },
                        status=424,
                    )
                else:
                    server.sync_members()
            return server

        def get_users_for_guild(guild: DiscordGuildSettings):
            opt_out_roles = guild.roles.filter(
                data__name__in=["NoLB", "TrainerDex Excluded"]
            ) | guild.roles.filter(exclude_roles_community_membership_discord__discord=guild)
            sq = Q()
            for x in opt_out_roles:
                sq |= Q(discordguildmembership__data__roles__contains=[str(x.id)])
            members = guild.members.exclude(sq)
            return Trainer.objects.filter(owner__socialaccount__in=members)

        def get_community(handle: str) -> Community:
            try:
                community = Community.objects.get(handle=handle)
            except Community.DoesNotExist:
                return Response(
                    {
                        "error": "Not Found",
                        "cause": "There is no known community with this handle.",
                        "solution": "Double check your spelling.",
                        "guild": handle,
                    },
                    status=404,
                )
            return community

        def get_users_for_community(community: Community):
            return community.get_members()

        def get_country(code: str) -> Dict:
            try:
                country_info = get_country_info(country.upper())
            except IndexError:
                return Response(
                    {
                        "error": "Not Found",
                        "cause": "There is no known country with this code.",
                        "solution": "Double check your spelling.",
                        "guild": code,
                    },
                    status=404,
                )
            return country_info

        def get_users_for_country(country: Dict):
            return Trainer.objects.filter(country_iso=country.upper())

        if guild:
            guild = get_guild(guild)
            if isinstance(guild, Response):
                return guild
            output = {"generated": generated_time, "stat": stat, "guild": guild.id}
            output["title"] = "{guild} Leaderboard".format(guild=guild)
            members = get_users_for_guild(guild)
        elif community:
            community = get_community(community)
            if isinstance(community, Response):
                return community
            output = {
                "generated": generated_time,
                "stat": stat,
                "community": community.handle,
            }
            output["title"] = "{community} Leaderboard".format(community=community)
            members = get_users_for_community(community)
        elif country:
            country = get_country(country)
            if isinstance(country, Response):
                return country
            output = {
                "generated": generated_time,
                "stat": stat,
                "country": country.get("code"),
            }
            output["title"] = "{country} Leaderboard".format(country=country.get("name"))
            members = get_users_for_country(country)
        else:
            output = {"generated": generated_time, "stat": stat, "title": None}
            members = Trainer.objects.all()

        query = filter_leaderboard_qs__update(Update.objects.filter(trainer__in=members))
        leaderboard = (
            Update.objects.filter(
                pk__in=Subquery(
                    query.filter(update_time__lte=generated_time)
                    .annotate(value=F(stat))
                    .exclude(value__isnull=True)
                    .order_by("trainer", "-value")
                    .distinct("trainer")
                    .values("pk")
                )
            )
            .select_related(
                "trainer",
                "trainer__owner",
            )
            .prefetch_related("trainer__nickname_set")
            .annotate(value=F(stat))
            .annotate(rank=Window(expression=DenseRank(), order_by=F("value").desc()))
            .order_by("rank", "-value", "update_time")
        )
        serializer = LeaderboardSerializer(leaderboard, many=True)
        output["aggregations"] = leaderboard.aggregate(
            avg=Avg("value"),
            count=Count("value"),
            min=Min("value"),
            max=Max("value"),
            sum=Sum("value"),
        )
        output["leaderboard"] = serializer.data
        return Response(output)
