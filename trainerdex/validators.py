from django.core import validators
from django.utils.translation import gettext_lazy as _, pgettext_lazy

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
