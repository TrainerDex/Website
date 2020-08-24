import datetime
from typing import Any, List, Iterable, Union

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from pokemongo.models import Trainer, Community
from pokemongo.shortcuts import filter_leaderboard_qs
from cities.models import Continent, Country, Region


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
        return filter_leaderboard_qs(Trainer.objects).distinct()

    def lastmod(self, obj: Trainer) -> datetime.datetime:
        return obj.last_modified

    def priority(self, obj: Trainer) -> float:
        return min(
            (
                min(
                    obj.update_set.exclude(total_xp__isnull=True)
                    .order_by("-total_xp")
                    .first()
                    .total_xp
                    / 20000000,
                    1.0,
                )
                * (5 / 11)
            )
            + 0.5,
            0.9,
        )


class LeaderboardContinentSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Continent.objects.exclude(code="AN")

    def location(self, obj: Continent) -> Any:
        return reverse("trainerdex:leaderboard", kwargs={"continent": obj.code})


class LeaderboardCountrySitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Country.objects.filter(
            leaderboard_trainers_country__isnull=False
        ).distinct()

    def priority(self, obj: Country) -> float:
        count = obj.leaderboard_trainers_country.count()
        if count:
            return 0.92 + min(count, 20) / 400
        else:
            return 0.02

    def location(self, obj: Country) -> Any:
        return reverse("trainerdex:leaderboard", kwargs={"country": obj.code})


class LeaderboardRegionSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Region.objects.filter(
            leaderboard_trainers_region__isnull=False
        ).distinct()

    def priority(self, obj: Region) -> float:
        count = obj.leaderboard_trainers_region.count()
        if count:
            return 0.92 + min(count, 20) / 400
        else:
            return 0.02

    def location(self, obj: Region) -> Any:
        return reverse(
            "trainerdex:leaderboard",
            kwargs={"country": obj.country.code, "region": obj.code},
        )


class LeaderboardCommunitySitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Community.objects.exclude(privacy_public=False).distinct()

    def priority(self, obj: Community) -> float:
        count = obj.get_members().count()
        if count:
            return min(0.74 + ((count / 1000) * 0.26), 1)
        else:
            return 0.74

    def location(self, obj: Community) -> Any:
        return reverse("trainerdex:leaderboard", kwargs={"community": obj.handle})
