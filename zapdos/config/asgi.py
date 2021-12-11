"""
ASGI config for TrainerDex project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from config import __version__
from config.settings import DEBUG

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test.settings")

application = get_asgi_application()

print("TrainerDex Version:", __version__)
if DEBUG:
    print("Running with Debug enabled")
