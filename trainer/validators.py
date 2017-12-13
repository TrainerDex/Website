from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_startdate(value):
	if value < date(2016, 7, 6):
		raise ValidationError(_('The date you picked was before launch date (6th July 2016).'), params={'value': value},)
