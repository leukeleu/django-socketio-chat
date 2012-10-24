import os
import sys

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from tornadio2 import router, server, conn, event
from tornado import web

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils.html import strip_tags

ROOT = os.path.normpath(os.path.dirname(__file__))


class ChatConnection(conn.SocketConnection):

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

        users = []
        for u in User.objects.all():
            u = {'id': u.id, 'username': u.username, 'firstName': u.first_name, 'lastName': u.last_name, 'online': u in self.logged_in_participants}
            users.append(u)
        self.emit('users', users)

    @event
    def public_message(self, message):
        message = strip_tags(message)
        for p in self.participants:
            p.emit('public_message', '%s' % self.user, message)

    @event
    def private_message(self, target_user, message):
        target_user = strip_tags(target_user)
        message = strip_tags(message)
        self.logged_in_participants[str(target_user)].emit('private_message', '%s' % self.user, '%s' % message)

    @event
    def leave(self):
        self.participants.remove(self)
        for p in self.participants:
            p.emit('user_left', '%s' % self.user)

    def on_disconnect(self):
        self.leave()

    def on_close(self):
        print 'close', self


class RouterConnection(conn.SocketConnection):
    __endpoints__ = {'/chat': ChatConnection}

    def on_open(self, info):
        print 'Router', repr(info)

        # store info for later use
        self.info = info


# Create chat server
ChatRouter = router.TornadioRouter(RouterConnection, dict(websocket_check=True), namespace='chat/socket.io')

# Create application
application = web.Application(
    ChatRouter.apply_routes([]),
    flash_policy_port = 843,
    flash_policy_file = os.path.join(ROOT, 'flashpolicy.xml'),
    socket_io_port = 8001
)

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    server.SocketServer(application)
