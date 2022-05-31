from __future__ import annotations

import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import F, Q, QuerySet, Subquery, Window, Max, Avg, Count, Min, Sum
from django.db.models.functions import DenseRank, Round
from django.utils import timezone
from rest_framework.request import Request

from pokemongo.api.v2.handlers.base import BaseHandler
from pokemongo.models import Update
from pokemongo.shortcuts import get_possible_levels_from_total_xp


class GlobalLeaderboardHandler(BaseHandler):
    def __init__(self, request: Request, *args, **kwargs) -> None:
        self.date_filter: datetime.date = datetime.date.fromisoformat(
            request.query_params.get(
                "date",
                datetime.date.today().isoformat(),
            )
        )
        self.field_filter: str = request.query_params.get("field", "total_xp")

    def get_queryset(self, *args, **kwargs) -> QuerySet[Update]:

        subquery = Subquery(
            Update.objects.alias(value=F(self.field_filter))
            .exclude(
                Q(trainer__owner__is_active=False)
                | Q(trainer__statistics=False)
                | Q(trainer__verified=False)
                | Q(trainer__last_cheated__gte=(self.date_filter - relativedelta(weeks=26)))
                | Q(
                    update_time__date__lt=(
                        self.date_filter
                        - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
                    )
                )
                | Q(update_time__date__gt=self.date_filter)
                | Q(value__isnull=True)
            )
            .filter(
                update_time__date__gte=(
                    self.date_filter
                    - relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)
                ),
                update_time__date__lte=self.date_filter,
                value__gt=0,
            )
            .order_by("trainer", "-value")
            .distinct("trainer")
            .values("pk")
        )

        query = (
            (
                Update.objects.filter(pk__in=subquery)
                .select_related("trainer")
                .annotate(
                    value=F(self.field_filter),
                    rank=Window(DenseRank(), order_by=F(self.field_filter).desc()),
                    max_total_xp=Max(
                        "total_xp",
                        filter=Q(trainer__uuid=F("trainer__uuid")),
                    ),
                )
            )
            .order_by("rank", "update_time")
            .only(
                "trainer__uuid",
                "trainer___nickname",
                "trainer__faction",
                "update_time",
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
                datetime=update.update_time.isoformat(),
                trainer=update.trainer.uuid,
            )
            for update in queryset
        ]

        output = dict(
            generated=timezone.now().isoformat(),
            date=self.date_filter.isoformat(),
            title="Global Leaderboard",
            field=self.field_filter,
            aggregations=aggregations,
            leaderboard=leaderboard,
        )

        return output
