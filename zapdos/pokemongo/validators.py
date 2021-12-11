import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PokemonGoUsernameValidator(validators.RegexValidator):
    regex = r"^[A-Za-z0-9]{3,15}$"
    message = _("Enter a valid username. This value may contain only English letters and numbers.")
    flags = re.ASCII


@deconstructible
class TrainerCodeValidator(validators.RegexValidator):
    regex = r"(\d{4}\s?){3}"
    message = _("Trainer Code must be 12 digits long and contain only numbers and whitespace.")
    flags = re.ASCII


username_validator = [PokemonGoUsernameValidator]


DATABASE_SOURCES = (
    ("?", None),
    ("cs_social_twitter", "Twitter (Found)"),
    ("cs_social_facebook", "Facebook (Found)"),
    ("cs_social_youtube", "YouTube (Found)"),
    ("cs_?", "Sourced Elsewhere"),
    ("ts_social_discord", "Discord"),
    ("ts_social_twitter", "Twitter"),
    ("ts_direct", "Directly told (via text)"),
    ("web_quick", "Quick Update (Web)"),
    ("web_detailed", "Detailed Update (Web)"),
    ("ts_registration", "Registration"),
    ("ss_registration", "Registration w/ Screenshot"),
    ("ss_generic", "Generic Screenshot"),
    ("ss_ocr", "OCR Screenshot"),
    ("com.nianticlabs.pokemongo.friends", "In Game Friends"),
    ("com.pokeassistant.trainerstats", "Poké Assistant"),
    ("com.pokenavbot.profiles", "PokeNav"),
    ("tl40datateam.spreadsheet", "Tl40 Data Team (Legacy)"),
    ("com.tl40data.website", "Tl40 Data Team"),
    ("com.pkmngots.import", "Third Saturday"),
)
