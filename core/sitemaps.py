import datetime
from typing import Any, List, Iterable, Union

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from pokemongo.models import Trainer, Community
from pokemongo.shortcuts import filter_leaderboard_qs
from cities.models import Country


class BaseSitemap(Sitemap):
    changefreq = "daily"

    def items(self) -> List[Iterable[Union[str, float]]]:
        return [
            ("account_settings", 0.9),
            ("trainerdex:leaderboard", 1),
            ("trainerdex:update_stats", 0.9),
        ]

    def priority(self, obj: Iterable[Union[str, float]]) -> float:
        return obj[1]

    def location(self, obj: Iterable[Union[str, float]]) -> Any:
        return reverse(obj[0])


class TrainerSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return (
            filter_leaderboard_qs(Trainer.objects)
            .order_by("id")
            .prefetch_related("update_set")
            .distinct()
        )

    def lastmod(self, obj: Trainer) -> datetime.datetime:
        return max(
            obj.last_modified, obj.update_set.only("update_time").latest("update_time").update_time
        )

    def priority(self, obj: Trainer) -> float:
        return 0.5


class LeaderboardCountrySitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Country.objects.filter(leaderboard_trainers_country__isnull=False).distinct()

    def priority(self, obj: Country) -> float:
        count = obj.leaderboard_trainers_country.count()
        if count:
            return 0.25 + (min(count, 100) / 200)
        else:
            return 0

    def location(self, obj: Country) -> Any:
        return reverse("trainerdex:leaderboard", kwargs={"country": obj.code})


class LeaderboardCommunitySitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Community.objects.exclude(privacy_public=False).order_by("handle").distinct()

    def priority(self, obj: Community) -> float:
        count = obj.get_members().count()
        if count:
            return 0.25 + (min(count, 100) / 200)
        else:
            return 0

    def location(self, obj: Community) -> Any:
        return reverse("trainerdex:leaderboard", kwargs={"community": obj.handle})
