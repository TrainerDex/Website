# -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

def PokemonGoUsernameValidator(value):
	match = re.match('^[A-Za-z0-9]{3,15}$', value)
	if not match:
		raise ValidationError(_("The username you entered is not a valid Pokemon Go username."), params={'value': value})

def TrainerCodeValidator(value):
	match = re.match('(\d{4}\s?){3}', value)
	if not match:
		raise ValidationError(_("Trainer Code must be 12 digits long and contain only numbers and whitespace."), params={'value': value})

username_validator = [PokemonGoUsernameValidator]
