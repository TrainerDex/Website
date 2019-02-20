# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy
from django.utils.translation import gettext_lazy as _
from django.core import validators

PokemonGoUsernameValidator = validators.RegexValidator(
    r'^[A-Za-z0-9]{3,15}$',
    pgettext_lazy("onboard_name_invalid_characters_error", "Only letters and numbers are allowed."),
    'invalid',
    )

TrainerCodeValidator = validators.RegexValidator(
    r'(\d{4}\s?){3}',
    _("Trainer Code must be 12 digits long and contain only numbers and whitespace."),
    'invalid',
    )

username_validator = [PokemonGoUsernameValidator]
