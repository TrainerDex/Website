import datetime
from typing import Any, Iterable, List, Union

from django.contrib.auth import get_user_model
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django_countries import Countries, countries
from pokemongo.models import Community
from pokemongo.utils import filter_leaderboard_qs

User = get_user_model()


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


class UserSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return (
            filter_leaderboard_qs(User.objects)
            .order_by("id")
            .prefetch_related("update_set")
            .distinct()
        )

    def lastmod(self, obj: User) -> datetime.datetime:
        return max(
            obj.last_modified,
            obj.update_set.only("post_dt").latest("post_dt").post_dt,
        )

    def priority(self, obj: User) -> float:
        return 0.5


# class LeaderboardCountrySitemap(Sitemap):
#     changefreq = "daily"

#     def items(self) -> Countries:
#         return countries

#     def location(self, obj: Country) -> Any:
#         return reverse("trainerdex:leaderboard", kwargs={"country": obj.code})


class LeaderboardCommunitySitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Community.objects.exclude(privacy_public=False).order_by("handle").distinct()

    def location(self, obj: Community) -> Any:
        return reverse("trainerdex:leaderboard", kwargs={"community": obj.handle})
