from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    gym_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    arrived = models.BooleanField(default=False)
