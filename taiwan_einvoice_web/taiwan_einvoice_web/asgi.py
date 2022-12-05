"""
ASGI config for taiwan_einvoice_web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import taiwan_einvoice.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taiwan_einvoice_web.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            taiwan_einvoice.routing.websocket_urlpatterns
        )
    ),
})
