import os
import sys

from datetime import datetime

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from tornadio2 import SocketConnection, TornadioRouter, SocketServer, event
from tornado import web

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils.html import strip_tags


def get_all_logged_in_users():
    import pdb; pdb.set_trace()

    return logged_in_user_ids


class ChatConnection(SocketConnection):

    connections = set()

    def on_open(self, info):
        """
        Find the Django user corresponding to this connection and send back useful chat info.
        """

        # get Django session
        cookie = info.get_cookie('sessionid')
        if cookie:
            # get User for session
            session = Session.objects.get(session_key=cookie.value)
            uid = session.get_decoded().get('_auth_user_id')
            try:
                self.user = User.objects.get(pk=uid)

                self.emit('welcome', self.user.username)
                self.connections.add(self)

                for connection in self.connections:
                    connection.emit('user_joined', self.user.username)

                users = []

                # find all logged in users
                sessions = Session.objects.filter(expire_date__gte=datetime.now())
                logged_in_user_ids = filter(None, list(set([ session.get_decoded().get('_auth_user_id') for session in sessions ])))

                for user in User.objects.all():
                    users.append({
                        'id': user.id, 'username': user.username, 'online': user.id in logged_in_user_ids
                    })
                self.emit('users', users)

            except User.DoesNotExist:
                pass

    @event
    def message(self, message):
        message = strip_tags(message)
        for connection in self.connections:
            connection.emit('message', self.user.username, message)

    @event
    def leave(self):
        self.connections.remove(self)
        for connection in self.connections:
            connection.emit('user_left', self.user.username)

    def on_disconnect(self):
        self.leave()

    def on_close(self):
        pass


# Create chat router
ChatRouter = TornadioRouter(ChatConnection, user_settings={'websocket_check': True}, namespace='chat/socket.io')

# Create application
application = web.Application(
    ChatRouter.apply_routes([]),
    socket_io_port = 8001,
)

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    SocketServer(application)
