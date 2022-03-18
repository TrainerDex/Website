from __future__ import annotations

import datetime
from typing import Iterable

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet
from django.urls import reverse

from pokemongo.models import Community, Trainer
from pokemongo.shortcuts import filter_leaderboard_qs


class BaseSitemap(Sitemap):
    changefreq = "daily"

    def items(self) -> Iterable[tuple[str, float]]:
        return [
            ("account_settings", 0.9),
            ("trainerdex:leaderboard", 1),
            ("trainerdex:update_stats", 0.9),
        ]

    def priority(self, obj: Iterable[tuple[str, float]]) -> float:
        return obj[1]

    def location(self, obj: Iterable[tuple[str, float]]) -> str:
        return reverse(obj[0])


class TrainerSitemap(Sitemap):
    changefreq = "weekly"

    def items(self) -> QuerySet[Trainer]:
        return (
            filter_leaderboard_qs(Trainer.objects)
            .order_by("id")
            .prefetch_related("update_set")
            .distinct()
        )

    def lastmod(self, obj: Trainer) -> datetime.datetime:
        return max(
            obj.updated_at,
            obj.update_set.only("update_time").latest("update_time").update_time,
        )

    def priority(self, obj: Trainer) -> float:
        return 0.5


class LeaderboardCommunitySitemap(Sitemap):
    changefreq = "daily"

    def items(self) -> QuerySet[Community]:
        return Community.objects.exclude(privacy_public=False).order_by("handle").distinct()

    def priority(self, obj: Community) -> float:
        count = obj.get_members().count()
        if count:
            return 0.25 + (min(count, 100) / 200)
        else:
            return 0.0

    def location(self, obj: Community) -> str:
        return reverse("trainerdex:leaderboard", kwargs={"community": obj.handle})
