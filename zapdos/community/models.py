import pytz

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import ExternalUUIDModel

# TODO: Spec out Community model


class Community(ExternalUUIDModel):
    # Identifying information
    handle = models.SlugField(unique=True)
    name = models.CharField(max_length=70)
    description = models.TextField(null=True, blank=True)

    base_language = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max([x[0] for x in settings.LANGUAGES], key=len)),
        blank=True,
        null=True,
        verbose_name=_("Language"),
        help_text=_(
            "The primary language of the community. This is used for all communications and leaderboard positions."
        ),
    )
    base_timezone = models.CharField(
        max_length=len(max(pytz.common_timezones, key=len)),
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_(
            "The primary timezone of the community. This is used for all communications and leaderboard positions."
        ),
    )

    privacy_public = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Viewable"),
        help_text=_(
            "By default, this is off." " Turn this on to share your community with the world."
        ),
    )
    privacy_public_join = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Joinable"),
        help_text=_(
            "By default, this is off."
            " Turn this on to make your community free to join."
            " No invites required."
        ),
    )

    memberships = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")
