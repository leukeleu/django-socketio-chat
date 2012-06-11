from os import path as op
import os, sys

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] == 'example.settings'

import tornado.web
import tornadio2
import tornadio2.router
import tornadio2.server
import tornadio2.conn

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

ROOT = op.normpath(op.dirname(__file__))


class ChatConnection(tornadio2.conn.SocketConnection):
    # Class level variable
    participants = set()

    def on_open(self, info):
        session_id = info.get_cookie('sessionid').value
        if session_id:
            # get user corresponding to session id
            session = Session.objects.get(session_key=session_id)
            uid = session.get_decoded().get('_auth_user_id')
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                user = 'Anonymous User'
        self.send("Welcome <b>%s</b> from the server." % user)
        self.participants.add(self)

    def on_message(self, message):
        # Pong message back
        for p in self.participants:
            p.send(message)

    def on_close(self):
        self.participants.remove(self)

# Create chat server
ChatRouter = tornadio2.router.TornadioRouter(ChatConnection, dict(websocket_check=True), namespace='chat/socket.io')

# Create application
application = tornado.web.Application(
    ChatRouter.apply_routes([]),
    flash_policy_port = 843,
    flash_policy_file = op.join(ROOT, 'flashpolicy.xml'),
    socket_io_port = 8001
)

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    tornadio2.server.SocketServer(application)
