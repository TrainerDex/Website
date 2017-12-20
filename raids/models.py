from django.db import models
from trainer.models import Trainer
from django.utils.translation import ugettext_lazy as _

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
		(INTERESTED, _('Interested')),
		(GOING, _('En Route')),
		(GOING_NOTLEFT, _('Will be there')),
		(GOING_LATE, _('Running late')),
		(ARRIVED, _('At the gym')),
		(COMPLETE, _('Completed')),
		(COMPLETE_CAUGHT, _('Completed (successful catch)')),
		(COMPLETE_RAN, _('Completed (boss ran)')),
		(FAILED, _('Failed to complete raid')),
		(ABORTED, _('No longer interested in raid')),
	)
	trainer = models.ForeignKey(Trainer)
	raid = models.ForeignKey(Raid)
	status = models.CharField(
		max_length=2,
		choices=ENROLLMENT_CHOICES,
	)
	
class Gym(models.Model):
	uuid = models.CharField(primary_key=True)