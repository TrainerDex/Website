from __future__ import annotations

import datetime
from abc import abstractmethod

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Count, F, Max, Min, Q, QuerySet, Subquery, Sum, Window
from django.db.models.functions import DenseRank
from django.utils import timezone
from isodate import date_isoformat, parse_date
from rest_framework.request import Request

from pokemongo.api.v2.serializers.leaderboard import SnapshotLeaderboardSerializer
from pokemongo.api.v2.views.leaderboard.interface import (
    LeaderboardMode,
    TrainerSubset,
    iLeaderboardView,
)
from pokemongo.models import Trainer, Update


class iSnapshotLeaderboardView(iLeaderboardView):
    MODE = LeaderboardMode.SNAPSHOT

    serializer_class = SnapshotLeaderboardSerializer

    @abstractmethod
    def get_leaderboard_title(self) -> str:
        ...

    def parse_args(self, request: Request) -> dict:
        self.args = dict(
            date=parse_date(request.query_params.get("date", datetime.date.today().isoformat())),
            stat=request.query_params.get("stat", "total_xp"),
            show_inactive=request.query_params.get("show_inactive", "false") == "true",
        )

    def get_data(self, request: Request):
        self.parse_args(request)

        trainer_subquery = Subquery(self.get_trainer_subquery().values("id"))
        subquery = Subquery(self.get_subquery(trainer_subquery).values("pk"))
        queryset = self.get_queryset(subquery)
        aggregate = self.aggregate_queryset(queryset)

        return {
            "generated": timezone.now(),
            "date": self.args["date"],
            "title": self.get_leaderboard_title(),
            "field": self.args["stat"],
            "aggregations": aggregate,
            "entries": queryset,
        }

    def get_trainer_subquery(self) -> QuerySet[Trainer]:
        return Trainer.objects.exclude(
            Q(owner__is_active=False)
            | Q(statistics=False)
            | Q(verified=False)
            | Q(last_cheated__gte=(self.args["date"] - relativedelta(weeks=26)))
        )

    def get_subquery(self, trainer_subquery: Subquery) -> QuerySet[Update]:
        return (
            Update.objects.alias(value=F(self.args["stat"]))
            .filter(trainer__id__in=trainer_subquery)
            .exclude(value__isnull=True)
            .filter(
                (
                    Q(
                        update_time__date__gte=(
                            self.args["date"]
                            - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
                        )
                    )
                    if not self.args["show_inactive"]
                    else Q()
                ),
                update_time__date__lte=self.args["date"],
                value__gt=0,
            )
            .order_by("trainer", "-value")
            .distinct("trainer")
        )

    def get_queryset(self, subquery: Subquery) -> QuerySet[Update]:
        return (
            Update.objects.filter(pk__in=subquery)
            .annotate(
                rank=Window(DenseRank(), order_by=F(self.args["stat"]).desc()),
                username=F("trainer___nickname"),
                faction=F("trainer__faction"),
                value=F(self.args["stat"]),
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

    def get_leaderboard_title(self) -> str:
        return "Global"
