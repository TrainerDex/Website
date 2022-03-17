import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class PrivateModel(models.Model):
    id = models.AutoField(_("ID"), primary_key=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    is_deleted = models.BooleanField(_("Deleted"), default=False)

    class Meta:
        abstract = True


class PublicModel(PrivateModel):
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True
