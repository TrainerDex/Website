from django.db import models
from trainer.models import Trainer

class Raid(models.Model):
    pokemon = models.PositiveIntegerField()
    gym = models.CharField(max_length=28)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    raiders = models.ManyToManyField(
        Trainer,
        through='Enrollment',
        through_fields=('raid','trainer'),
    )

class Enrollment(models.Model):
    INTERESTED = 'I'
    GOING = 'G'
    GOING_NOTLEFT = 'G-'
    GOING_LATE = 'GL'
    ARRIVED = 'A'
    COMPLETE = 'D'
    COMPLETE_CAUGHT = 'DC'
    COMPLETE_RAN = 'DR'
    FAILED = 'X'
    ABORTED = '/'
    ENROLLMENT_CHOICES = (
        (INTERESTED, 'Interested'),
        (GOING, 'En Route'),
        (GOING_NOTLEFT, 'Will be there'),
        (GOING_LATE, 'Running late'),
        (ARRIVED, 'At the gym'),
        (COMPLETE, 'Completed'),
        (COMPLETE_CAUGHT, 'Completed (successful catch)'),
        (COMPLETE_RAN, 'Completed (boss ran)'),
        (FAILED, 'Failed to complete raid'),
        (ABORTED, 'No longer interested in raid'),
    )
    trainer = models.ForeignKey(Trainer)
    raid = models.ForeignKey(Raid)
    status = models.CharField(
        max_length=2,
        choices=ENROLLMENT_CHOICES,
    )