"""ASGI config for SiBekas."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sibekas.settings")

application = get_asgi_application()
