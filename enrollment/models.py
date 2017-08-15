from django.db import models
from django.conf import settings

# Create your models here.
class Enrollment(models.Model):
    discord_id = models.IntegerField(unique=True, primary_key=True)
    gym_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    arrived = models.BooleanField(default=False)
