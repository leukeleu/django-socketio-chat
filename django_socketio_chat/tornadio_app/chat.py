from os import path as op
import os
import sys

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] == 'example.settings'

import tornado.web
import tornadio2
import tornadio2.router
import tornadio2.server
import tornadio2.conn
from tornadio2.conn import SocketConnection
from tornadio2 import event

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

ROOT = op.normpath(op.dirname(__file__))


class ChatConnection(SocketConnection):

    participants = set()
    logged_in_participants = {}
    user = 'anonymous'

    def on_open(self, info):
        """
        Try to find the Django user corresponding to this chat connection and
        send back useful chat info.
        """
        router_info = self.session.conn.info

        # get Django session
        session_id = router_info.get_cookie('sessionid')
        if session_id:
            if session_id:
                session_id = session_id.value
            # get user corresponding to session id
            session = Session.objects.get(session_key=session_id)
            uid = session.get_decoded().get('_auth_user_id')
            try:
                self.user = User.objects.get(pk=uid)
                self.logged_in_participants[str(self.user)] = self
            except User.DoesNotExist:
                pass

        self.emit('welcome', '%s' % self.user)
        self.participants.add(self)

        for p in self.participants:
            p.emit('user_joined', '%s' % self.user)

        users = {}
        for u in User.objects.all():
            users[str(u)] = str(u) in self.logged_in_participants

        self.emit('users', users)

    def on_message(self, message):
        for p in self.participants:
            p.send(message)

    @event
    def private_message(self, user, message):
        self.logged_in_participants[str(user)].send('<b>Private</b> %s says: %s' % (self.user, message))

    def on_close(self):
        self.participants.remove(self)
        for p in self.participants:
            p.emit('user_left', '%s' % self.user)


class RouterConnection(SocketConnection):
    __endpoints__ = {'/chat': ChatConnection}

    def on_open(self, info):
        print 'Router', repr(info)

        # store info for later use
        self.info = info


# Create chat server
ChatRouter = tornadio2.router.TornadioRouter(RouterConnection, dict(websocket_check=True), namespace='chat/socket.io')

# Create application
application = tornado.web.Application(
    ChatRouter.apply_routes([]),
    flash_policy_port=843,
    flash_policy_file=op.join(ROOT, 'flashpolicy.xml'),
    socket_io_port=8001
)

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    tornadio2.server.SocketServer(application)
