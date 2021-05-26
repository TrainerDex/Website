"""
WSGI config for ekpogo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from trainerdex import __version__

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trainerdex.settings")

application = get_wsgi_application()

print("TrainerDex Version:", __version__)
