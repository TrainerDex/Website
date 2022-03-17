from collections import Counter
import logging
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class PrivateModel(models.Model):
    id = models.AutoField(_("ID"), primary_key=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    is_deleted = models.BooleanField(_("Deleted"), default=False)
    deleted_at = models.DateTimeField(_("Deleted at"), null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, *args, **kwargs) -> Counter[dict[str, int]]:
        if self.is_deleted:
            return Counter()

        self.updated_at = kwargs.get("updated_at") or now()
        self.deleted_at = kwargs.get("updated_at") or now()
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at", "deleted_at"])
        logger.debug(
            "%(model)s %(id)s soft-deleted at %(updated_at)s",
            (str(self._meta), self.pk, self.updated_at),
        )
        return Counter({str(self._meta): 1})

    def undelete(self, *args, **kwargs) -> Counter[dict[str, int]]:
        if not self.is_deleted:
            return Counter()

        self.updated_at = kwargs.get("updated_at") or now()
        self.deleted_at = None
        self.is_deleted = False
        self.save(update_fields=["is_deleted", "updated_at", "deleted_at"])
        logger.debug(
            "%(model)s %(id)s undeleted at %(updated_at)s",
            (str(self._meta), self.pk, self.updated_at),
        )
        return Counter({str(self._meta): 1})


class PublicModel(PrivateModel):
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True
