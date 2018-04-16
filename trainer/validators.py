# -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def StartDateValidator(value):
	LAUNCH_DATE = date(2016, 7, 6)
	if not date.today()+timedelta(days=1) >= value >= LAUNCH_DATE:
		raise ValidationError(_("The date you entered was before launch date of {launch_date} or in the future.").format(launch_date=LAUNCH_DATE), params={'value': value},)

def PokemonGoUsernameValidator(value):
	if not (4 <= len(value) <= 15):
		raise ValidationError(_("The username you entered is not a valid Pokemon Go username."), params={'value': value},)

username_validator = [PokemonGoUsernameValidator]
