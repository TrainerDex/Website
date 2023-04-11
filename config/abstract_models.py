from collections import Counter
from datetime import datetime
from uuid import UUID, uuid4

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class PrivateModel(models.Model):
    id: int = models.AutoField("ID", primary_key=True)
    created_at: datetime = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at: datetime = models.DateTimeField(_("Updated at"), auto_now=True)
    is_deleted: bool = models.BooleanField(_("Deleted"), default=False)
    deleted_at: datetime | None = models.DateTimeField(_("Deleted at"), null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, *args, **kwargs) -> Counter[dict[str, int]]:
        if self.is_deleted:
            return Counter()

        self.updated_at = kwargs.get("updated_at") or now()
        self.deleted_at = kwargs.get("updated_at") or now()
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at", "deleted_at"])
        return Counter({str(self._meta): 1})

    def undelete(self, *args, **kwargs) -> Counter[dict[str, int]]:
        if not self.is_deleted:
            return Counter()

        self.updated_at = kwargs.get("updated_at") or now()
        self.deleted_at = None
        self.is_deleted = False
        self.save(update_fields=["is_deleted", "updated_at", "deleted_at"])
        return Counter({str(self._meta): 1})


class PublicModel(PrivateModel):
    uuid: UUID = models.UUIDField("UUID", default=uuid4, unique=True, editable=False)

    class Meta:
        abstract = True
