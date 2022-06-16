from __future__ import annotations

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet

from pokemongo.models import Trainer


def get_discord_trainer_query(dt: datetime, guild_id: int) -> QuerySet[Trainer]:
    return Trainer.objects.exclude(
        Q(owner__is_active=False)
        | Q(statistics=False)
        | Q(verified=False)
        | Q(last_cheated__gte=(dt - relativedelta(weeks=26)))
    ).filter(owner__socialaccount__guilds__id=guild_id)
