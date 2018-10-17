# -*- coding: utf-8 -*-
from rest_framework.exceptions import ValidationError, ParseError
from django.utils.translation import gettext_lazy as _

def ThrowMalformedPKError(request, *args, **kwargs):
    raise ParseError("Expected a Numeric ID, didn't.")

def ThrowMalformedUUIDError(request, *args, **kwargs):
    raise ParseError("Expected a UUID, didn't.")
