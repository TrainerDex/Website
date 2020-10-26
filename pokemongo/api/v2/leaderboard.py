import datetime
import logging
from typing import Dict, Optional, Union

from django.db.models import Avg, Count, F, Max, Min, Prefetch, Q, Subquery, Sum, Window
from django.db.models.functions import DenseRank
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

import requests
from cities.models import Country

from pokemongo.api.v2.paginator import LeaderboardPagination
from pokemongo.models import Community, Trainer, Update, Nickname
from pokemongo.shortcuts import filter_leaderboard_qs__update, level_parser, UPDATE_FIELDS_BADGES
from core.models import DiscordGuildSettings, get_guild_info

logger = logging.getLogger("django.trainerdex")

VALID_LB_STATS = UPDATE_FIELDS_BADGES + (
    "pokedex_caught",
    "pokedex_seen",
    "total_xp",
)


class LeaderboardSerializer(serializers.Serializer):
    level = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    trainer_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    faction = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    update_time = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_position(self, obj: Update) -> int:
        return obj.rank

    def get_level(self, obj: Update) -> Optional[int]:
        try:
            return level_parser(xp=obj.total_xp).level
        except ValueError:
            return None

    def get_trainer_id(self, obj: Update) -> int:
        return obj.trainer.id

    def get_username(self, obj: Update) -> str:
        return obj.trainer.nickname

    def get_faction(self, obj: Update) -> int:
        return obj.trainer.faction

    def get_value(self, obj: Update) -> int:
        return obj.value

    def get_update_time(self, obj: Update) -> datetime.datetime:
        return obj.datetime

    def get_user_id(self, obj: Update) -> int:
        return obj.trainer.owner.pk if obj.trainer.owner else None

    class Meta:
        model = Update
        fields = (
            "position",
            "trainer_id",
            "username",
            "faction",
            "level",
            "stat",
            "update_time",
            "user_id",
        )


class LeaderboardView(ListAPIView):

    serializer_class = LeaderboardSerializer
    pagination_class = LeaderboardPagination

    def get_paginated_response(self, data, **kwargs):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, **kwargs)

    def get_guild(self, guild: int) -> DiscordGuildSettings:
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

    def get_users_for_guild(self, guild: DiscordGuildSettings):
        opt_out_roles = guild.roles.filter(
            data__name__in=["NoLB", "TrainerDex Excluded"]
        ) | guild.roles.filter(exclude_roles_community_membership_discord__discord=guild)
        sq = Q()
        for x in opt_out_roles:
            sq |= Q(discordguildmembership__data__roles__contains=[str(x.id)])
        members = guild.members.exclude(sq)
        return Trainer.objects.filter(owner__socialaccount__in=members)

    def get_community(self, handle: str) -> Community:
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

    def get_users_for_community(self, community: Community):
        return community.get_members()

    def get_country(self, code: str) -> Country:
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

    def get_users_for_country(self, country: Country):
        return country.leaderboard_trainers_country.all()

    def get_queryset(self, *args, **kwargs):
        if kwargs.get("guild"):
            guild = self.get_guild(kwargs.get("guild"))
            members = self.get_users_for_guild(guild)
        elif kwargs.get("community"):
            community = self.get_community(kwargs.get("community"))
            members = self.get_users_for_community(community)
        elif kwargs.get("country"):
            country = self.get_country(kwargs.get("country"))
            members = self.get_users_for_country(country)
        else:
            members = Trainer.objects.all()

        return filter_leaderboard_qs__update(Update.objects.filter(trainer__in=members))

    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        dt = timezone.now()
        stat = kwargs.get("stat", "total_xp")

        if kwargs.get("guild"):
            guild = self.get_guild(kwargs.get("guild"))
            if isinstance(guild, Response):
                return guild
            output = {
                "generated": dt,
                "stat": stat,
                "guild": guild.id,
            }
            output["title"] = "{guild} Leaderboard".format(guild=guild)
        elif kwargs.get("community"):
            community = self.get_community(kwargs.get("community"))
            if isinstance(community, Response):
                return community
            output = {"generated": dt, "stat": stat, "community": community.handle}
            output["title"] = "{community} Leaderboard".format(community=community)
        elif kwargs.get("country"):
            country = self.get_country(kwargs.get("country"))
            if isinstance(country, Response):
                return country
            output = {"generated": dt, "stat": stat, "country": country.code}
            output["title"] = "{country} Leaderboard".format(country=country)
        else:
            output = {"generated": dt, "stat": stat, "title": None}

        query = self.get_queryset(*args, **kwargs)
        leaderboard = (
            Update.objects.filter(
                pk__in=Subquery(
                    query.filter(update_time__lte=dt)
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
        serializer = self.serializer_class(self.paginate_queryset(leaderboard), many=True)
        return self.get_paginated_response(serializer.data, **output)

    def get(self, request, *args, **kwargs):
        if not kwargs.get("stat"):
            kwargs["stat"] = "total_xp"
        if kwargs.get("stat") not in VALID_LB_STATS:
            return Response(
                {"state": "error", "reason": "invalid stat"}, status=status.HTTP_400_BAD_REQUEST
            )
        return self.list(request, *args, **kwargs)
