"""
ASGI config for the backend project.

This configuration file sets up the ASGI application for handling both HTTP and WebSocket requests. 
ASGI (Asynchronous Server Gateway Interface) is a standard for Python asynchronous web apps and servers to communicate.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from backend.consumers import ChatConsumer

# Set the default settings module for the 'django' command-line environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Define the ASGI application
# The application is configured to handle both HTTP and WebSocket protocols
application = ProtocolTypeRouter(
    {
        # HTTP requests are handled by Django's ASGI application
        "http": get_asgi_application(),
        # WebSocket requests are handled by Channels
        "websocket": AllowedHostsOriginValidator(
            # AuthMiddlewareStack automatically adds Django's session authentication to the connection
            AuthMiddlewareStack(
                # URLRouter allows routing based on the WebSocket URL patterns
                URLRouter(
                    [
                        # Define the WebSocket path for chat rooms
                        path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
                    ]
                )
            )
        ),
    }
)
