from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/view_messages/(?P<room_name>[\w\d-]+)/$',
            consumers.MessagesConsumer.as_asgi())
]
