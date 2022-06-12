from __future__ import annotations

from datetime import datetime

from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    OuterRef,
    QuerySet,
    Subquery,
    Window,
    Case,
    When,
)
from django.db.models.functions import ExtractDay, ExtractSecond, DenseRank

from pokemongo.models import Trainer, Update


def get_queryset_for_diffboard(
    trainer_queryset: QuerySet[Trainer],
    dt1: datetime,
    dt2: datetime,
    stat: str,
    dt0: datetime = None,
) -> QuerySet[Trainer]:

    if dt0 is None:
        dt0 = dt1 - (dt2 - dt1)

    queryset = (
        trainer_queryset.annotate(
            dt1=Subquery(
                Update.objects.annotate(value=F(stat))
                .filter(
                    trainer__id=OuterRef("id"),
                    update_time__lte=dt1,
                    update_time__gt=dt0,
                    value__isnull=False,
                )
                .order_by("-update_time")
                .values("update_time")[:1]
            ),
            value1=Subquery(
                Update.objects.annotate(value=F(stat))
                .filter(
                    trainer__id=OuterRef("id"),
                    update_time__lte=dt1,
                    update_time__gt=dt0,
                    value__isnull=False,
                )
                .order_by("-update_time")
                .values("value")[:1]
            ),
            dt2=Subquery(
                Update.objects.annotate(value=F(stat))
                .filter(
                    trainer__id=OuterRef("id"),
                    update_time__lte=dt2,
                    update_time__gt=dt1,
                    value__isnull=False,
                )
                .order_by("-update_time")
                .values("update_time")[:1]
            ),
            value2=Subquery(
                Update.objects.annotate(value=F(stat))
                .filter(
                    trainer__id=OuterRef("id"),
                    update_time__lte=dt2,
                    update_time__gt=dt1,
                    value__isnull=False,
                )
                .order_by("-update_time")
                .values("value")[:1]
            ),
            dtdiff=F("dt2") - F("dt1"),
            valuediff=F("value2") - F("value1"),
            diffrate=ExpressionWrapper(
                F("valuediff") / (ExtractDay("dtdiff") + (ExtractSecond("dtdiff") / 86400)),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
        )
        .exclude(Q(dt1__isnull=True) & Q(dt2__isnull=True))
        .annotate(
            rank=Case(
                When(
                    Q(dt1__isnull=False) & Q(dt2__isnull=False),
                    Window(
                        DenseRank(),
                        order_by=F("diffrate").desc(nulls_last=True),
                    ),
                )
            ),
        )
        .order_by("rank", "value2", "value1")
        .values(
            "rank",
            "uuid",
            "_nickname",
            "dt1",
            "value1",
            "dt2",
            "value2",
            "dtdiff",
            "valuediff",
            "diffrate",
        )
    )
    return queryset
