import os
import logging

from tornadio2 import TornadioRouter, SocketServer
from tornado import web

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'

from django_socketio_chat.tornadio_app import chat

logging.getLogger().setLevel(logging.INFO)

# Create chat router
ChatRouter = TornadioRouter(chat.ChatConnection,
                            user_settings={'websocket_check': True},
                            namespace='chat/socket.io')

# Create application
application = web.Application(
    ChatRouter.apply_routes([]),
    socket_io_port=8001,
)

SocketServer(application)


