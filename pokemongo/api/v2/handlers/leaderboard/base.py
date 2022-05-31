from __future__ import annotations

import datetime
from typing import Iterable

from dateutil.relativedelta import relativedelta
from django.db.models import (
    Avg,
    Count,
    F,
    Max,
    Min,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Window,
)
from django.db.models.functions import DenseRank, Round
from django.utils import timezone
from rest_framework.request import Request

from pokemongo.api.v2.handlers.base import BaseHandler
from pokemongo.models import Trainer, Update
from pokemongo.shortcuts import LEVELS, Level, get_possible_levels_from_total_xp


class BaseLeaderboardHandler(BaseHandler):
    def __init__(self, request: Request, *args, **kwargs) -> None:
        self.date_filter: datetime.date = datetime.date.fromisoformat(
            request.query_params.get(
                "date",
                datetime.date.today().isoformat(),
            )
        )
        self.field_filter: str = request.query_params.get("field", "total_xp")

        if factions := request.query_params.get("factions"):
            self.faction_filters: Iterable[int] = [int(x) for x in factions.split(",")]
        else:
            self.faction_filters = None

        self.level__gte = (
            int(level__gte)
            if (level__gte := request.query_params.get("level__gte", None))
            else None
        )
        self.level__lte = (
            int(level__lte)
            if (level__lte := request.query_params.get("level__lte", None))
            else None
        )

        self.value__gte = (
            float(value__gte)
            if (value__gte := request.query_params.get("value__gte", None))
            else None
        )
        self.value__lte = (
            float(value__lte)
            if (value__lte := request.query_params.get("value__lte", None))
            else None
        )

        self.show_inactive = request.query_params.get("show_inactive") == "true"

    def get_leaderboard_title(self) -> str:
        ...

    def get_trainer_subquery(self) -> QuerySet[Trainer]:
        return Trainer.objects.exclude(
            Q(owner__is_active=False)
            | Q(statistics=False)
            | Q(verified=False)
            | Q(last_cheated__gte=(self.date_filter - relativedelta(weeks=26)))
        )

    @staticmethod
    def get_level(level: int) -> Level:
        return LEVELS[level - 1]

    def get_queryset(self, *args, **kwargs) -> QuerySet[Update]:
        subquery = (
            Update.objects.alias(value=F(self.field_filter))
            .filter(trainer__id__in=Subquery(self.get_trainer_subquery().values("id")))
            .exclude(value__isnull=True)
            .filter(
                (
                    Q(
                        update_time__date__gte=(
                            self.date_filter
                            - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
                        )
                    )
                    if not self.show_inactive
                    else Q()
                ),
                update_time__date__lte=self.date_filter,
                value__gt=0,
            )
            .filter(
                Q(trainer__faction__in=self.faction_filters) if self.faction_filters else Q(),
            )
            .order_by("trainer", "-value")
            .distinct("trainer")
            .values("pk")
        )

        query = (
            Update.objects.filter(pk__in=Subquery(subquery))
            .select_related("trainer")
            .annotate(
                value=F(self.field_filter),
                rank=Window(DenseRank(), order_by=F(self.field_filter).desc()),
                max_total_xp=Subquery(
                    Update.objects.filter(
                        trainer_id=OuterRef("trainer_id"),
                        update_time__lte=OuterRef("update_time"),
                        total_xp__isnull=False,
                    )
                    .order_by("-total_xp")
                    .values("total_xp")[:1]
                ),
            )
            .exclude(
                (
                    Q(max_total_xp__lt=self.get_level(self.level__gte).total_xp)
                    if self.level__gte
                    else Q()
                )
                | (
                    Q(
                        max_total_xp__gt=(
                            (level := self.get_level(self.level__lte)).total_xp + level.xp_required
                        )
                    )
                    if self.level__lte and self.level__lte < 50
                    else Q()
                )
                | (Q(value__lt=self.value__gte) if self.value__gte else Q())
                | (Q(value__gt=self.value__lte) if self.value__lte else Q())
            )
            .order_by("rank", "update_time")
            .only(
                "trainer__uuid",
                "trainer___nickname",
                "trainer__faction",
                "update_time",
                "uuid",
            )
        )
        return query[:1000]

    def format_data(self, queryset: QuerySet[Update], *args, **kwargs) -> dict:
        aggregations = queryset.aggregate(
            avg=Round(Avg("value"), 2),
            count=Round(Count("value"), 2),
            min=Round(Min("value"), 2),
            max=Round(Max("value"), 2),
            sum=Round(Sum("value"), 2),
        )

        guess_level = (
            lambda xp: str(min(levels))
            if len((levels := [x.level for x in get_possible_levels_from_total_xp(xp=xp)])) == 1
            else f"{min(levels)}-{max(levels)}"
        )

        leaderboard = [
            dict(
                rank=update.rank,
                username=update.trainer._nickname,
                faction=update.trainer.faction,
                level=guess_level(update.max_total_xp) if update.max_total_xp else None,
                value=update.value,
                trainer_uuid=str(update.trainer.uuid),
                entry_uuid=str(update.uuid),
                entry_time=update.update_time.isoformat(),
            )
            for update in queryset
        ]

        output = dict(
            generated=timezone.now().isoformat(),
            date=self.date_filter.isoformat(),
            title=self.get_leaderboard_title(),
            field=self.field_filter,
            aggregations=aggregations,
            leaderboard=leaderboard,
        )

        return output
