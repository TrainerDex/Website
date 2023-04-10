from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, F, Max, Min, Q, QuerySet, Subquery, Sum, Window
from django.db.models.functions import DenseRank
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_countries import countries
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import authentication, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.models.discord import DiscordGuild
from core.permissions import IsStaffOrReadOnlyOrTokenHasScope
from pokemongo.api.v1.serializers import (
    DetailedTrainerSerializer,
    DetailedUpdateSerializer,
    LatestStatsSerializer,
    LeaderboardSerializer,
    SocialAllAuthSerializer,
    UserSerializer,
)
from pokemongo.fields import BaseStatistic
from pokemongo.models import Community, Trainer, Update
from pokemongo.shortcuts import OLD_NEW_STAT_MAP, filter_leaderboard_qs__update

logger = logging.getLogger(f"trainerdex.website.{__name__}")

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


def recent(value: datetime) -> bool:
    if timezone.now() - timedelta(hours=1) <= value <= timezone.now():
        return True
    return False


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = (
        User.objects.select_related("trainer")
        .exclude(is_active=False)
        .only("id", "username", "trainer__uuid", "trainer__id")
    )
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TrainerListView(APIView):
    """
    get:
    Accepts paramaters for Team (t) and Nickname (q)

    post:
    Register a Trainer, needs the Primary Key of the Owner, the User object which owns the Trainer
    """

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read"]],
    }

    def get(self, request: Request) -> Response:
        queryset = Trainer.objects.prefetch_related("update_set").exclude(owner__is_active=False)

        if not request.user.is_superuser:
            queryset = queryset.exclude(statistics=False)

        if nickname_filter := request.query_params.get("q"):
            queryset = queryset.filter(nickname__nickname__iexact=nickname_filter)

        if team_filter := request.query_params.get("t"):
            queryset = queryset.filter(faction=team_filter)

        serializer = DetailedTrainerSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """
        This used to work as a simple post, but since the beginning of transitioning to API v2 it would have always given Validation Errors if left the same.
        Now it has a 60 minute open slot to work after the auth.User (owner) instance is created. After which, a PATCH request must be given. This is due to the nature of a Trainer being created automatically for all new auth.User
        """

        trainer: Trainer = Trainer.objects.prefetch_related("update_set").get(
            owner__pk=request.data["owner"], owner__is_active=True
        )
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

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read"]],
        "PATCH": [["write"]],
    }

    def get_object(self, pk: int) -> Trainer:
        try:
            return (
                Trainer.objects.exclude(owner__is_active=False)
                .prefetch_related("update_set")
                .select_related("owner")
                .get(pk=pk)
            )
        except Trainer.DoesNotExist:
            raise Http404("No %s matches the given query." % Trainer._meta.object_name)

    def get(self, request: Request, pk: int) -> Response:
        trainer = self.get_object(pk)
        if trainer.active and (trainer.statistics or request.user.is_superuser):
            serializer = DetailedTrainerSerializer(trainer)
            return Response(serializer.data)
        elif (not trainer.active) or (not trainer.statistics):
            response = {
                "code": 1,
                "reason": "Profile deactivated",
                "profile": {"id": trainer.pk},
            }
            return Response(response, status=status.HTTP_423_LOCKED)
        return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request: Request, pk: int) -> Response:
        trainer = self.get_object(pk)
        serializer = DetailedTrainerSerializer(trainer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int) -> Response:
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

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read"]],
        "POST": [["write"]],
        "PATCH": [["write"]],
    }

    def get(self, request: Request, pk: int) -> Response:
        updates = Update.objects.filter(trainer=pk, trainer__owner__is_active=True)
        serializer = DetailedUpdateSerializer(updates, many=True)
        return Response(serializer.data)

    def post(self, request: Request, pk: int) -> Response:
        modified_data = {
            OLD_NEW_STAT_MAP.get(key, key): value for key, value in request.data.items()
        }
        serializer = DetailedUpdateSerializer(data=modified_data)
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

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read"]],
        "PATCH": [["write"]],
    }

    def get(self, request: Request, pk: int) -> Response:
        try:
            update = Update.objects.filter(trainer=pk, trainer__owner__is_active=True).latest(
                "update_time"
            )
        except Update.DoesNotExist:
            return Response(None, status=404)
        serializer = DetailedUpdateSerializer(update)
        return Response(serializer.data)

    def patch(self, request: Request, pk: int) -> Response:
        update = Update.objects.filter(trainer=pk, trainer__owner__is_active=True).latest(
            "update_time"
        )
        if update.created_at > (timezone.now() - timedelta(hours=12)):
            modified_data = {
                OLD_NEW_STAT_MAP.get(key, key): value for key, value in request.data.items()
            }
            serializer = DetailedUpdateSerializer(update, data=modified_data)
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
    Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked
    """

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read"]],
        "PATCH": [["write"]],
    }

    def get(self, request: Request, uuid: str, pk: int) -> Response:
        update = get_object_or_404(Update, trainer=pk, uuid=uuid, trainer__owner__is_active=True)
        serializer = DetailedUpdateSerializer(update)
        if update.trainer.id != int(pk):
            return Response(status=400)
        return Response(serializer.data)

    def patch(self, request: Request, uuid: str, pk: int) -> Response:
        update = get_object_or_404(Update, trainer=pk, uuid=uuid, trainer__owner__is_active=True)
        if update.created_at > (timezone.now() - timedelta(hours=12)):
            modified_data = {
                OLD_NEW_STAT_MAP.get(key, key): value for key, value in request.data.items()
            }
            serializer = DetailedUpdateSerializer(update, data=modified_data)
            if serializer.is_valid():
                serializer.save(trainer=update.trainer, uuid=update.uuid, pk=update.pk)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LatestStatsView(APIView):
    """
    get:
    Gets detailed view of the latest update

    patch:
    Allows editting of update within 12 hours of creation, after that time, all updates are denied.
    Trainer, UUID and PK are locked.
    """

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read"]],
    }

    def get(self, request: Request, pk: int) -> Response:
        latest_stats = Trainer.objects.filter(pk=pk).aggregate(
            **{
                field.name: Max(
                    f"update__{field.name}",
                    filter=Q(**{f"update__{field.name}__isnull": False}),
                )
                for field in (
                    Update.get_sortable_fields() + [Update._meta.get_field("update_time")]
                )
            },
        )
        serializer = LatestStatsSerializer(latest_stats)
        return Response(serializer.data)


class SocialLookupView(APIView):
    """
    get:
        kwargs:
            provider (requiered) - platform, options are 'twitter', 'discord', 'reddit'

            uid - Social ID, supports a comma seperated list. Could be useful for passing a list of users in a server to retrieve a list of UserIDs, which could then be passed to api/v1/leaderboard/
            user - TrainerDex User ID, supports a comma seperated list
            trainer - TrainerDex Trainer ID

    put:
        Register a SocialAccount. Patch if exists, post if not.
    """

    authentication_classes = (authentication.TokenAuthentication, OAuth2Authentication)
    permission_classes = [IsStaffOrReadOnlyOrTokenHasScope]
    required_alternate_scopes = {
        "GET": [["read:social"]],
        "PUT": [["write:social"]],
    }

    def get(self, request: Request) -> Response:
        query = SocialAccount.objects.exclude(user__is_active=False).filter(
            provider=request.query_params.get("provider")
        )
        if request.query_params.get("uid"):
            query = query.filter(uid__in=request.query_params.get("uid").split(","))
        elif request.query_params.get("user"):
            query = query.filter(user__in=request.query_params.get("user").split(","))
        elif request.query_params.get("trainer"):
            query = query.filter(user__trainer=request.query_params.get("trainer"))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SocialAllAuthSerializer(query, many=True)
        return Response(serializer.data)

    def put(self, request: Request) -> Response:
        try:
            query = SocialAccount.objects.exclude(user__is_active=False).get(
                provider=request.data["provider"], uid=request.data["uid"]
            )
        except SocialAccount.DoesNotExist:
            serializer = SocialAllAuthSerializer(data=request.data)
        else:
            serializer = SocialAllAuthSerializer(query, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailedLeaderboardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(
        self,
        request: Request,
        stat: int = "total_xp",
        guild: int = None,
        community: str = None,
        country: str = None,
    ) -> Response:
        stat = OLD_NEW_STAT_MAP.get(stat, stat)

        if (
            not isinstance(field := Update._meta.get_field(stat), BaseStatistic)
            or not field.sortable
        ):
            return Response(
                {"state": "error", "reason": "invalid stat"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        generated_time = timezone.now()

        def get_guild(guild: int) -> DiscordGuild:
            try:
                server = DiscordGuild.objects.get(id=guild)
            except DiscordGuild.DoesNotExist:
                logger.warn(f"Guild with id {guild} not found")
                server = DiscordGuild(id=guild)
                server.refresh_from_api()
                if not server.has_access:
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
                    server.sync_members()

            if not server.data or server.outdated:
                server.refresh_from_api()

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

        def get_users_for_guild(guild: DiscordGuild) -> QuerySet[Trainer]:
            opt_out_roles = (
                guild.roles.filter(data__name__in=["NoLB", "TrainerDex Excluded"])
                | guild.roles.filter(exclude_roles_community_membership_discord__discord=guild)
            ).only("id")

            queryset = Trainer.objects.filter(owner__socialaccount__guilds__id=guild.id)

            if opt_out_roles:
                queryset = queryset.exclude(
                    owner__socialaccount__guild_memberships__data__roles__contains=[
                        str(x.id) for x in opt_out_roles
                    ]
                )

            return queryset

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

        def get_users_for_country(country: Dict):
            return Trainer.objects.filter(country=country.upper())

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
            country_name = dict(countries).get(country.upper())
            if country_name is None:
                return Response(
                    {
                        "error": "Not Found",
                        "cause": "There is no known country with this code.",
                        "solution": "Double check your spelling.",
                        "guild": country.upper(),
                    },
                    status=404,
                )
            output = {
                "generated": generated_time,
                "stat": stat,
                "country": country,
            }
            output["title"] = f"{country_name} Leaderboard"
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
            .select_related("trainer__owner")
            .annotate(value=F(stat))
            .annotate(rank=Window(expression=DenseRank(), order_by=F("value").desc()))
            .order_by("rank", "update_time")
            .only(
                "total_xp",
                "trainer_level",
                "trainer__id",
                "trainer___nickname",
                "trainer__faction",
                "update_time",
                "trainer__owner__id",
            )
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
