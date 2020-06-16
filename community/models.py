import logging
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from pytz import common_timezones

from core.models import DiscordGuild
from trainerdex.models import Trainer


class Community(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="UUID",
        )
    language = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max(settings.LANGUAGES, key=lambda x: len(x[0]))[0]),
        )
    timezone = models.CharField(
        default=settings.TIME_ZONE,
        choices=((x,x) for x in common_timezones),
        max_length=len(max(common_timezones, key=len)),
        )
    name = models.CharField(
        max_length=70,
        )
    description = models.TextField(
        null=True,
        blank=True,
        )
    handle = models.SlugField(
        unique=True,
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
    privacy_tournaments = models.BooleanField(
        default=False,
        verbose_name=_("Tournament: Publicly Viewable"),
        help_text=_("By default, this is off. Turn this on to share your tournament results with the world."),
        )

    memberships_personal = models.ManyToManyField(
        Trainer,
        blank=True,
        )
    memberships_discord = models.ManyToManyField(
        DiscordGuild,
        through='CommunityMembershipDiscord',
        through_fields=('community', 'discord'),
        blank=True,
        )

    def __str__(self):
        return self.name
    
    def get_members(self):
        qs = self.memberships_personal.all()
        
        for x in CommunityMembershipDiscord.objects.filter(sync_members=True, community=self):
            qs |= x.members_queryset()
        
        return qs
    
    def get_absolute_url(self):
        return reverse('trainerdex:leaderboard', kwargs={'community':self.handle})
    
    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")

class CommunityMembershipDiscord(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        )
    discord = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        )
    
    sync_members = models.BooleanField(
        default=True,
        help_text=_("Members in this Discord are automatically included in the community."),
        )
    include_roles = models.ManyToManyField(
        DiscordRole,
        related_name='include_roles_community_membership_discord',
        blank=True,
        )
    exclude_roles = models.ManyToManyField(
        DiscordRole,
        related_name='exclude_roles_community_membership_discord',
        blank=True,
        )

    def __str__(self):
        return "{community} - {guild}".format(community=self.community, guild=self.discord)
    
    def members_queryset(self):
        if self.sync_members:
            qs =  Trainer.objects.exclude(owner__is_active=False) \
                .filter(owner__socialaccount__discordguildmembership__guild__communitymembershipdiscord=self)
            
            if self.include_roles.exists():
                q = models.Q()
                for role in self.include_roles.all():
                    q = q | models.Q(owner__socialaccount__discordguildmembership__data__roles__contains=str(role.id))
                qs = qs.filter(q)
            
            if self.exclude_roles.exists():
                q = models.Q()
                for role in self.exclude_roles.all():
                    q = q | models.Q(owner__socialaccount__discordguildmembership__data__roles__contains=str(role.id))
                qs = qs.exclude(q)
            
            return qs
        else:
            return Trainer.objects.none()

    class Meta:
        verbose_name = _("Community Discord Connection")
        verbose_name_plural = _("Community Discord Connections")
