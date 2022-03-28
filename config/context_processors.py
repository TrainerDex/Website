from typing import Dict

from django import __version__ as django_version

from config import __version__ as tdx_version


def version(request) -> Dict[str, str]:
    return {"tdx_version": tdx_version, "django_version": django_version}
