from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, npgettext_lazy
from pytz import common_timezones

from trainerdex.models import Trainer


class Community(models.Model):
    handle = models.SlugField(
        primary_key=True,
        editable=False,
    )
    language = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max(dict(settings.LANGUAGES).keys(), key=len)),
    )
    timezone = models.CharField(
        default=settings.TIME_ZONE,
        choices=((x, x) for x in common_timezones),
        max_length=len(max(common_timezones, key=len)),
    )
    name = models.CharField(
        max_length=70,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )

    privacy_public = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Viewable"),
        help_text=_("By default, this is off. Turn this on to share your community with the world."),
    )
    privacy_public_join = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Joinable"),
        help_text=_("By default, this is off. Turn this on to make your community free to join. No invites required."),
    )

    members = models.ManyToManyField(
        Trainer,
        blank=True,
    )

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('trainerdex:leaderboard', kwargs={'community': self.handle})
    
    class Meta:
        verbose_name = npgettext_lazy("community__title", "community", "communities", 1)
        verbose_name_plural = npgettext_lazy("community__title", "community", "communities", 2)
