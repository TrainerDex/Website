from __future__ import annotations

from abc import abstractmethod

from dateutil.relativedelta import relativedelta
from django.db.models import (
    Avg,
    Case,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Max,
    Min,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    When,
    Window,
)
from django.db.models.functions import DenseRank, ExtractDay, ExtractSecond
from django.utils import timezone
from isodate import parse_date, parse_duration
from rest_framework.request import Request

from pokemongo.api.v2.serializers.leaderboard import GainLeaderboardSerializer
from pokemongo.api.v2.views.leaderboard.interface import (
    LeaderboardMode,
    TrainerSubset,
    iLeaderboardView,
)
from pokemongo.models import Trainer, Update


class iGainLeaderboardView(iLeaderboardView):
    MODE = LeaderboardMode.GAIN

    serializer_class = GainLeaderboardSerializer

    @abstractmethod
    def get_leaderboard_title(self) -> str:
        ...

    def parse_args(self, request: Request) -> dict:
        assert (subtrahend_date_str := request.query_params.get("subtrahend_date"))
        assert (minuend_date_str := request.query_params.get("minuend_date"))
        duration_str = request.query_params.get("duration")

        self.args = dict(
            subtrahend_date=parse_date(subtrahend_date_str),
            minuend_date=parse_date(minuend_date_str),
            stat=request.query_params.get("stat", "total_xp"),
        )
        self.args["duration"] = (
            parse_duration(duration_str)
            if duration_str
            else (self.args["minuend_date"] - self.args["subtrahend_date"])
        )

    def get_data(self, request: Request):
        self.parse_args(request)

        trainer_queryset = self.get_trainer_queryset()
        queryset = self.get_queryset(trainer_queryset)
        aggregate = self.aggregate_queryset(queryset)

        return {
            "generated": timezone.now().isoformat(),
            "subtrahend_date": self.args["subtrahend_date"],
            "minuend_date": self.args["minuend_date"],
            "duration": self.args["duration"],
            "title": self.get_leaderboard_title(),
            "stat": self.args["stat"],
            "aggregations": aggregate,
            "entries": queryset,
        }

    def get_trainer_queryset(self) -> QuerySet[Trainer]:
        return Trainer.objects.exclude(
            Q(owner__is_active=False)
            | Q(statistics=False)
            | Q(verified=False)
            | Q(last_cheated__gte=(self.args["subtrahend_date"] - relativedelta(weeks=26)))
        )

    def get_queryset(self, trainer_queryset: QuerySet[Trainer]) -> QuerySet[Trainer]:
        stat: str = self.args["stat"]
        subtrahend_daterange = (
            self.args["subtrahend_date"] - self.args["duration"],
            self.args["subtrahend_date"],
        )
        minuend_daterange = (
            self.args["minuend_date"] - self.args["duration"],
            self.args["minuend_date"],
        )

        return (
            trainer_queryset.annotate(
                subtrahend_datetime=Subquery(
                    Update.objects.annotate(value=F(self.args["stat"]))
                    .filter(
                        trainer__id=OuterRef("id"),
                        update_time__gt=subtrahend_daterange[0],
                        update_time__lte=subtrahend_daterange[1],
                        value__isnull=False,
                    )
                    .order_by("-update_time")
                    .values("update_time")[:1]
                ),
                subtrahend_value=Subquery(
                    Update.objects.annotate(value=F(stat))
                    .filter(
                        trainer__id=OuterRef("id"),
                        update_time=OuterRef("subtrahend_datetime"),
                        value__isnull=False,
                    )
                    .order_by("-update_time")
                    .values("value")[:1]
                ),
                minuend_datetime=Subquery(
                    Update.objects.annotate(value=F(stat))
                    .filter(
                        trainer__id=OuterRef("id"),
                        update_time__gt=minuend_daterange[0],
                        update_time__lte=minuend_daterange[1],
                        value__isnull=False,
                    )
                    .order_by("-update_time")
                    .values("update_time")[:1]
                ),
                minuend_value=Subquery(
                    Update.objects.annotate(value=F(stat))
                    .filter(
                        trainer__id=OuterRef("id"),
                        update_time=OuterRef("minuend_datetime"),
                        value__isnull=False,
                    )
                    .order_by("-update_time")
                    .values("value")[:1]
                ),
                difference_duration=F("minuend_datetime") - F("subtrahend_datetime"),
                difference_value=F("minuend_value") - F("subtrahend_value"),
                difference_value_rate=ExpressionWrapper(
                    F("difference_value")
                    / (
                        ExtractDay("difference_duration")
                        + (ExtractSecond("difference_duration") / 86400)
                    ),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                difference_value_percentage=ExpressionWrapper(
                    (F("difference_value") / F("subtrahend_value")) * 100,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .exclude(Q(subtrahend_datetime=True) & Q(minuend_datetime=True))
            .annotate(
                rank=Case(
                    When(
                        Q(subtrahend_datetime=False) & Q(minuend_datetime=False),
                        Window(
                            DenseRank(),
                            order_by=F("difference_value_rate").desc(nulls_last=True),
                        ),
                    )
                ),
            )
            .order_by("rank", "minuend_value", "subtrahend_value")
            .values(
                "rank",
                "uuid",
                "_nickname",
                "subtrahend_datetime",
                "subtrahend_value",
                "minuend_datetime",
                "minuend_value",
                "difference_duration",
                "difference_value",
                "difference_value_rate",
                "difference_value_percentage",
            )
        )

    def aggregate_queryset(self, queryset: QuerySet[Update]) -> dict:
        return queryset.aggregate(
            trainer_count=Count("uuid"),
            average_rate=Avg("difference_value_rate"),
            min_rate=Min("difference_value_rate"),
            max_rate=Max("difference_value_rate"),
            average_change=Avg("difference_value"),
            min_change=Min("difference_value"),
            max_change=Max("difference_value"),
            sum_change=Sum("difference_value"),
        )


class GainLeaderboardView(iGainLeaderboardView):
    SUBSET = TrainerSubset.GLOBAL

    authentication_classes = []
    permission_classes = []

    def get_leaderboard_title(self) -> str:
        return "Global"
