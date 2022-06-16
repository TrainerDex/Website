from __future__ import annotations
from abc import abstractmethod

import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import F, Q, QuerySet, Subquery, Window, Avg, Count, Sum, Min, Max
from django.db.models.functions import DenseRank
from django.utils import timezone
from rest_framework.request import Request

from pokemongo.api.v2.views.leaderboard.interface import (
    LeaderboardMode,
    TrainerSubset,
    iLeaderboardView,
)
from pokemongo.api.v2.serializers.leaderboard import SnapshotLeaderboardSerializer
from pokemongo.models import Trainer, Update


class iSnapshotLeaderboardView(iLeaderboardView):
    MODE = LeaderboardMode.SNAPSHOT

    serializer = SnapshotLeaderboardSerializer

    @abstractmethod
    def get_leaderboard_title(self, arguments: dict) -> str:
        ...

    def parse_args(self, request: Request) -> dict:
        return dict(
            date=datetime.date.fromisoformat(
                request.query_params.get("date", datetime.date.today().isoformat())
            ),
            stat=request.query_params.get("stat", "total_xp"),
            show_inactive=request.query_params.get("show_inactive", "false") == "true",
        )

    def get_data(self, request: Request):
        arguments = self.parse_args(request)

        trainer_subquery = Subquery(self.get_trainer_subquery(arguments).values("id"))
        subquery = Subquery(self.get_subquery(arguments, trainer_subquery).values("pk"))
        queryset = self.get_queryset(arguments, subquery)
        aggregate = self.aggregate_queryset(queryset)

        return {
            "generated": timezone.now().isoformat(),
            "date": arguments["date"],
            "title": self.get_leaderboard_title(arguments),
            "field": arguments["stat"],
            "aggregations": aggregate,
            "entries": queryset,
        }

    def get_trainer_subquery(self, arguments: dict) -> QuerySet[Trainer]:
        return Trainer.objects.exclude(
            Q(owner__is_active=False)
            | Q(statistics=False)
            | Q(verified=False)
            | Q(last_cheated__gte=(arguments["date"] - relativedelta(weeks=26)))
        )

    def get_subquery(self, arguments: dict, trainer_subquery: Subquery) -> QuerySet[Update]:
        return (
            Update.objects.alias(value=F(arguments["stat"]))
            .filter(trainer__id__in=trainer_subquery)
            .exclude(value__isnull=True)
            .filter(
                (
                    Q(
                        update_time__date__gte=(
                            arguments["date"]
                            - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
                        )
                    )
                    if not arguments["show_inactive"]
                    else Q()
                ),
                update_time__date__lte=arguments["date_"],
                value__gt=0,
            )
            .order_by("trainer", "-value")
            .distinct("trainer")
        )

    def get_queryset(self, arguments: dict, subquery: Subquery) -> QuerySet[Update]:
        return (
            Update.objects.filter(pk__in=subquery)
            .annotate(
                rank=Window(DenseRank(), order_by=F(arguments["stat"]).desc()),
                username=F("trainer___nickname"),
                faction=F("trainer__faction"),
                value=F(arguments["stat"]),
                trainer_uuid=F("trainer__uuid"),
                entry_uuid=F("uuid"),
                entry_datetime=F("update_time"),
            )
            .order_by("rank", "entry_datetime")
        )

    def aggregate_queryset(self, queryset: QuerySet[Update]) -> dict:
        return queryset.aggregate(
            average=Avg("value"),
            count=Count("value"),
            min=Min("value"),
            max=Max("value"),
            sum=Sum("value"),
        )


class SnapshotLeaderboardView(iSnapshotLeaderboardView):
    SUBSET = TrainerSubset.GLOBAL

    authentication_classes = []
    permission_classes = []

    def get_leaderboard_title(self, _) -> str:
        return "Global"
