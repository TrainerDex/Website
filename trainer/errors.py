from rest_framework.exceptions import ValidationError, ParseError

def ThrowMalformedPKError(request, *args, **kwargs):
    raise ParseError("Expected a Numeric ID, got gibberish.")

def ThrowMalformedUUIDError(request, *args, **kwargs):
    raise ParseError("Expected a UUID, got gibberish.")
