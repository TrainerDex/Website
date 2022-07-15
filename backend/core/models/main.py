from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from config.abstract_models import PublicModel


class Service(PublicModel):
    name = models.CharField(verbose_name=_("name"), max_length=32)
    description = models.TextField(verbose_name=_("description"), blank=True)

    def __str__(self):
        return self.name

    def get_status(self) -> ServiceStatus:
        return self.statuses.latest("created_at")


class StatusChoices(models.TextChoices):
    UP = "UP", _("Up")
    DOWN = "DOWN", _("Down")
    UNSTABLE = "UNSTABLE", _("Unstable")
    MAINTENANCE = "MAINTENANCE", _("Scheduled Maintenance")
    UNKNOWN = "UNKNOWN", _("Unknown")


class ServiceStatus(PublicModel):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name=_("service"),
        related_name="statuses",
    )
    status = models.CharField(
        choices=StatusChoices.choices,
        max_length=len(max(StatusChoices.values, key=len)),
        verbose_name=_("status"),
    )
    reason = models.TextField(verbose_name=_("reason"), blank=True)

    def __str__(self):
        return f"{self.service} is {self.status}"
