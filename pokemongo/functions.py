import datetime
from pokemongo.models import Trainer

LEVEL_40_BADGE_ASSIGNMENT_DATE = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)


def set_legacy_40_badges():
    queryset = (
        Trainer.objects.filter(
            update__update_time__lt=LEVEL_40_BADGE_ASSIGNMENT_DATE,
            update__total_xp__gte=20_000_000,
        )
        .order_by("pk")
        .distinct("pk")
    )
    return queryset.update(legacy_40=True)
