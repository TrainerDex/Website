import logging
from datetime import datetime

from django.db.models import Avg, Count, F, Max, Min, Prefetch, Q, Subquery, Sum, Window
from django.db.models.functions import DenseRank
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import requests
from cities.models import Country

from pokemongo.models import Community, Trainer, Update, Nickname
from pokemongo.api.v1.serializers import LeaderboardSerializer
from pokemongo.shortcuts import filter_leaderboard_qs__update, UPDATE_FIELDS_BADGES
from core.models import DiscordGuildSettings, get_guild_info

logger = logging.getLogger("django.trainerdex")

VALID_LB_STATS = UPDATE_FIELDS_BADGES + (
    "pokedex_caught",
    "pokedex_seen",
    "total_xp",
)


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
                {"state": "error", "reason": "invalid stat"}, status=status.HTTP_400_BAD_REQUEST
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
                {"state": "error", "reason": "invalid stat"}, status=status.HTTP_400_BAD_REQUEST
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

        def get_country(code: str) -> Country:
            try:
                country = Country.objects.prefetch_related("leaderboard_trainers_country").get(
                    code__iexact=code
                )
            except Country.DoesNotExist:
                return Response(
                    {
                        "error": "Not Found",
                        "cause": "There is no known country with this code.",
                        "solution": "Double check your spelling.",
                        "guild": code,
                    },
                    status=404,
                )
            return country

        def get_users_for_country(country: Country):
            return country.leaderboard_trainers_country.all()

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
            output = {"generated": generated_time, "stat": stat, "community": community.handle}
            output["title"] = "{community} Leaderboard".format(community=community)
            members = get_users_for_community(community)
        elif country:
            country = get_country(country)
            if isinstance(country, Response):
                return country
            output = {"generated": generated_time, "stat": stat, "country": country.code}
            output["title"] = "{country} Leaderboard".format(country=country)
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
