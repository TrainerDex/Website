from __future__ import annotations

from abc import abstractmethod
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Case, DecimalField, ExpressionWrapper, F, Max, Min, Q, QuerySet, Sum, When, Window
from django.db.models.functions import DenseRank, ExtractDay, ExtractSecond
from django.utils import timezone
from isodate import parse_duration
from rest_framework.request import Request

from pokemongo.api.v2.paginators.leaderboard import GainLeaderboardPaginator
from pokemongo.api.v2.views.leaderboard.interface import LeaderboardMode, TrainerSubset, iLeaderboardView
from pokemongo.models import Trainer, Update


class iGainLeaderboardView(iLeaderboardView):
    MODE = LeaderboardMode.GAIN

    pagination_class = GainLeaderboardPaginator

    @abstractmethod
    def get_leaderboard_title(self) -> str:
        ...

    def parse_args(self, request: Request) -> dict:
        assert (
            subtrahend_datetime_str := request.query_params.get("subtrahend_datetime")
        ), "subtrahend_datetime is required"
        assert (minuend_datetime_str := request.query_params.get("minuend_datetime")), "minuend_datetime is required"
        duration_str = request.query_params.get("duration")

        self.subtrahend_datetime = datetime.fromisoformat(subtrahend_datetime_str)
        self.minuend_datetime = datetime.fromisoformat(minuend_datetime_str)
        self.stat = request.query_params.get("stat", "total_xp")

        assert self.minuend_datetime > self.subtrahend_datetime, "minuend_datetime must be after subtrahend_datetime"

        self.duration = (
            parse_duration(duration_str) if duration_str else (self.minuend_datetime - self.subtrahend_datetime)
        )

    def get_data(self, request: Request):
        self.parse_args(request)

        trainer_queryset = self.get_trainer_queryset()
        queryset = self.get_queryset(trainer_queryset)
        aggregate = self.aggregate_queryset(queryset)

        page: list = self.paginate_queryset(queryset)

        return {
            "generated_datetime": timezone.now().isoformat(),
            "subtrahend_datetime": self.subtrahend_datetime,
            "minuend_datetime": self.minuend_datetime,
            "duration": self.duration,
            "title": self.get_leaderboard_title(),
            "stat": self.stat,
            "aggregations": aggregate,
            "entries": page,
        }

    def get_trainer_queryset(self) -> QuerySet[Trainer]:
        return Trainer.objects.exclude(
            Q(owner__is_active=False)
            | Q(statistics=False)
            | Q(verified=False)
            | Q(last_cheated__gte=(self.subtrahend_datetime - relativedelta(weeks=26)))
        )

    def get_queryset(self, trainer_queryset: QuerySet[Trainer]) -> QuerySet[Trainer]:
        stat: str = self.stat
        subtrahend_daterange = (
            self.subtrahend_datetime - self.duration,
            self.subtrahend_datetime,
        )
        minuend_daterange = (
            self.minuend_datetime - self.duration,
            self.minuend_datetime,
        )

        return (
            trainer_queryset.annotate(
                subtrahend_datetime=Max(
                    F("update__update_time"),
                    filter=(
                        Q(update__update_time__range=subtrahend_daterange) & Q(**{f"update__{stat}__isnull": False})
                    ),
                ),
                subtrahend_value=Max(
                    F(f"update__{stat}"),
                    filter=(
                        Q(update__update_time__range=subtrahend_daterange) & Q(**{f"update__{stat}__isnull": False})
                    ),
                ),
                minuend_datetime=Max(
                    F("update__update_time"),
                    filter=(
                        Q(update__update_time__range=minuend_daterange) & Q(**{f"update__{stat}__isnull": False})
                    ),
                ),
                minuend_value=Max(
                    F(f"update__{stat}"),
                    filter=(
                        Q(update__update_time__range=minuend_daterange) & Q(**{f"update__{stat}__isnull": False})
                    ),
                ),
                difference_duration=F("minuend_datetime") - F("subtrahend_datetime"),
                difference_value=F("minuend_value") - F("subtrahend_value"),
                difference_value_rate=ExpressionWrapper(
                    F("difference_value")
                    / (ExtractDay("difference_duration") + (ExtractSecond("difference_duration") / 86400)),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                difference_value_percentage=ExpressionWrapper(
                    (F("difference_value") / F("subtrahend_value")) * 100,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .exclude(Q(subtrahend_datetime__isnull=True) & Q(minuend_datetime__isnull=True))
            .annotate(
                rank=Case(
                    When(
                        Q(subtrahend_datetime__isnull=False) & Q(minuend_datetime__isnull=False),
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
