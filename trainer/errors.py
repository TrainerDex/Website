from rest_framework.exceptions import ValidationError, ParseError
from django.utils.translation import ugettext_lazy as _

def ThrowMalformedPKError(request, *args, **kwargs):
    raise ParseError(_("Expected a Numeric ID, got gibberish."))

def ThrowMalformedUUIDError(request, *args, **kwargs):
    raise ParseError(_("Expected a UUID, got gibberish."))
