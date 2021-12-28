from __future__ import annotations
import datetime
import pytz
import uuid
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_countries import CountryTuple
from django_countries.fields import CountryField
from exclusivebooleanfield.fields import ExclusiveBooleanField
from model_utils.managers import InheritanceManager

from pokemongo.validators import PokemonGoUsernameValidator, TrainerCodeValidator

if TYPE_CHECKING:
    from pokemongo.models import Faction, FactionAlliance


class BaseModel(models.Model):
    """
    Base model for all models
    """

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"

    def __str__(self) -> str:
        return self.__repr__()

    class Meta:
        abstract = True


class ExternalUUIDModel(BaseModel):
    """
    Base model for all models that have an external UUID
    """

    external_uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        verbose_name=_("External UUID"),
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id} External: {self.external_uuid}>"

    class Meta:
        abstract = True


class User(AbstractUser, ExternalUUIDModel):
    username: str = models.CharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        error_messages={"unique": _("This username is already taken.")},
        verbose_name=_("Username"),
        help_text=_(
            "Required. 15 characters or fewer. Letters and digits only. Must match your Pokémon Go username."
        ),
    )

    timezone: str = models.CharField(
        max_length=len(max(pytz.common_timezones, key=len)),
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_("The timezone of the user"),
    )
    country: CountryTuple = CountryField(
        verbose_name=_("Country"), help_text=_("The country of the user")
    )

    is_public: bool = models.BooleanField(
        default=True,
        verbose_name=_("Public"),
        help_text=_("Whether this User's profile is public"),
    )
    is_perma_banned: bool = models.BooleanField(
        default=False, verbose_name=_("Banned"), help_text=_("Whether this user is banned")
    )
    is_verified: bool = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Whether this User's account has been verified"),
    )

    last_caught_cheating: datetime.date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last Cheated"),
        help_text=_("When did this Trainer last cheat?"),
    )
    legacy_level_40: bool = models.BooleanField(
        default=False,
        verbose_name=pgettext_lazy("badge_level_40_title", "Legacy 40"),
        help_text=pgettext_lazy("badge_level_40", "Achieve level 40 before 2020-12-31"),
    )

    pogo_date_created: datetime.date = models.DateField(
        null=True,
        blank=True,
        validators=[MinValueValidator(datetime.date(2016, 7, 5))],
        verbose_name=pgettext_lazy("profile_start_date", "Start Date"),
        help_text=_("The date this user created their Pokémon Go account"),
    )
    faction_alliances: models.ManyToManyField[FactionAlliance] = models.ManyToManyField(
        related_name="members",
        through="pokemongo.FactionAlliance",
        through_fields=("user", "faction"),
        to="pokemongo.Faction",
        verbose_name=_("Faction Alliances"),
    )
    trainer_code: str = models.CharField(
        null=True,
        blank=True,
        validators=[TrainerCodeValidator],
        max_length=15,
        verbose_name=pgettext_lazy("friend_code_title", "Trainer Code"),
        help_text=_("Fancy sharing your trainer code?"),
    )

    # TODO: Make goals it's own thing
    daily_goal: int = models.PositiveIntegerField(null=True, blank=True)
    total_goal: int = models.BigIntegerField(
        null=True, blank=True, validators=[MinValueValidator(100)]
    )

    def has_cheated(self) -> bool:
        return bool(self.last_caught_cheating)

    has_cheated.boolean = True

    def timezone_to_python(self) -> pytz.BaseTzInfo:
        return pytz.timezone(self.timezone)

    def get_alliance(self) -> FactionAlliance:
        try:
            return self.faction_alliances.through.objects.filter(
                date_disbanded__isnull=True
            ).latest("date_aligned")
        except self.faction_alliances.through.DoesNotExist:
            from pokemongo.models import DummyFactionAlliance

            return DummyFactionAlliance(self)

    def faction(self) -> Faction:
        return self.get_alliance().faction

    def is_banned(self, date: datetime.date = None) -> bool:
        if self.is_perma_banned:
            return True

        if date is None:
            date = timezone.now().date()

        if self.last_caught_cheating:
            return self.last_caught_cheating + datetime.timedelta(weeks=26) > date

    is_banned.boolean = True

    def get_absolute_url(self) -> str:
        return reverse("trainerdex:profile", kwargs={"nickname": self.username})

    def __str__(self) -> str:
        return f"{self.username} (\U0001F194: {self.id})"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [
            ("can_verify", "Can verify users"),
            ("can_ban", "Can ban users"),
            ("can_unban", "Can unban users"),
            ("can_view_private_profile", "Can view private profiles"),
            ("can_view_public_profile", "Can view public profiles"),
        ]


class UsernameHistory(ExternalUUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="username_history")
    username = models.CharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        error_messages={"unique": _("This username is already taken.")},
        verbose_name=_("Username"),
        help_text=_(
            "Required. 15 characters or fewer. Letters and digits only. Must match your Pokémon Go username."
        ),
    )

    date_assigned = models.DateField(blank=True, null=True)
    currently_assigned = ExclusiveBooleanField(on="user")

    def update_usermodel(self):
        self.user: User
        self.user.username = self.username
        self.user.save(update_fields="username")

    def save(self, *args, **kwargs) -> None:
        if self.currently_assigned:
            self.update_usermodel()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.username} ({self.user})"

    class Meta:
        verbose_name = _("Username")
        verbose_name_plural = _("Usernames")
        order_with_respect_to = "user"


class FeedPost(ExternalUUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="posts",
    )
    post_dt = models.DateTimeField(
        default=timezone.now,
    )
    metadata = models.JSONField(
        default=dict,
        verbose_name=_("Metadata"),
        help_text=_("Any metadata about the post, such as program that made the post etc."),
        blank=True,
        null=True,
    )
    body = models.CharField(max_length=240, blank=True)

    objects = InheritanceManager()

    # The plan is to create a dedicated model for this, but for now it's commented out.
    # I need to work out a good plan for storing media, and I don't want to do that now.
    # attached_media = models.ForeignKey()

    class Meta:
        verbose_name = _("Feed Post")
        verbose_name_plural = _("Feed Posts")
        ordering = ["-post_dt"]
