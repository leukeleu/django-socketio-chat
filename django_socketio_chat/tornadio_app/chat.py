import os
import sys

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from tornadio2 import SocketConnection, TornadioRouter, SocketServer, event
from tornado import web

from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from django_socketio_chat.models import Chat, ChatSession, UserChatStatus
from django_socketio_chat import serializers
from django_socketio_chat.utils import prepare_for_emit


class ChatConnection(SocketConnection):

    connections = {}
    chat_session = None

    def on_open(self, info):
        """
        Send the user all the relevant chat info if the user has a valid Django session.
        """

        # get Django session
        cookie = info.get_cookie('sessionid')
        if cookie:
            # get User for session
            try:
                session = Session.objects.get(session_key=cookie.value)
                user_id = session.get_decoded().get('_auth_user_id')
                # `store` user with connection
                self.user = User.objects.get(pk=user_id)
            except (User.DoesNotExist, Session.DoesNotExist):
                return
            else:
                # TODO Implement a __hash__ method on this class?
                self.connections[self.user] = self.connections.get(self.user, set())
                self.connections[self.user].add(self)

                self.chat_session, created = ChatSession.objects.get_or_create(user=self.user)
                chat_session_obj = prepare_for_emit(serializers.ChatSessionSerializer(self.chat_session).data)

                if self.chat_session.status == self.chat_session.SIGNED_OFF:
                    self.emit('ev_chat_session_status', chat_session_obj)
                    return

                elif self.chat_session.status == self.chat_session.SIGNED_IN:
                    self.send_all_chat_info()

    def send_all_chat_info(self):
        chat_session_obj = prepare_for_emit(serializers.ChatSessionSerializer(self.chat_session).data)
        chat_users = self.chat_session.users_that_i_see
        chat_users_obj = prepare_for_emit(serializers.UserSerializer(chat_users).data)

        chats = self.chat_session.chats
        chats_obj = prepare_for_emit(serializers.ChatSerializer(chats).data)

        self.emit('ev_data_update', chat_session_obj, chat_users_obj, chats_obj)

    @event('req_user_sign_in')
    def sign_in(self):
        if self.chat_session.is_signed_in:
            return
        self.chat_session.sign_in()
        self.send_all_chat_info()
        for user in self.chat_session.users_that_see_me:
            chat_users = ChatSession.objects.get(user=user).users_that_i_see
            chat_users_obj = prepare_for_emit(serializers.UserSerializer(chat_users).data)
            for connection in self.connections.get(user, []):
                connection.emit('ev_user_signed_in', self.user.username, chat_users_obj)

    @event('req_user_sign_off')
    def sign_off(self):
        self.chat_session.sign_off()
        for user in self.chat_session.users_that_see_me:
            chat_users = ChatSession.objects.get(user=user).users_that_i_see
            chat_users_obj = prepare_for_emit(serializers.UserSerializer(chat_users).data)
            for connection in self.connections.get(user, []):
                connection.emit('ev_user_signed_off', self.user.username, chat_users_obj)
        chat_session_obj = prepare_for_emit(serializers.ChatSessionSerializer(self.chat_session).data)
        self.emit('ev_chat_session_status', chat_session_obj)

    @event('req_user_go_invisible')
    def go_invisible(self):
        self.chat_session.go_invisible()
        for user in self.chat_session.users_that_see_me:
            chat_users = ChatSession.objects.get(user=user).users_that_i_see
            chat_users_obj = prepare_for_emit(serializers.UserSerializer(chat_users).data)
            for connection in self.connections.get(user, []):
                connection.emit('ev_user_signed_off', self.user.username, chat_users_obj)

    @event('req_chat_create')
    def chat_create(self, username):
        user = User.objects.get(username=username)
        if user in self.chat_session.users_that_i_see:
            chat = Chat.start(self.user, [user])
            chat_obj = prepare_for_emit(serializers.ChatSerializer(chat).data)
            for user in chat.users.all():
                for connection in self.connections.get(user, []):
                    connection.emit('ev_chat_created', chat_obj)

    @event('req_chat_add_user')
    def chat_add_user(self, chat_uuid, username):
        chat = Chat.objects.get(uuid=chat_uuid)
        user = User.objects.get(username=username)
        if user in self.chat_session.users_that_i_see and self.user in chat.users.all() and user not in chat.users.all():
            chat.add_users([user])
            chat_obj = prepare_for_emit(serializers.ChatSerializer(chat).data)

            # send chat obj to new user
            for connection in self.connections.get(user, []):
                connection.emit('ev_you_were_added', chat_obj)

            # notify all users in chat
            for user in chat.users.all():
                for connection in self.connections.get(user, []):
                    connection.emit('ev_chat_user_added', chat.uuid.hex, username)

    @event('req_message_send')
    def message_send(self, message_body, chat_uuid):
        chat = Chat.objects.get(uuid=chat_uuid)

        if not self.user in chat.users.all():
            return

        message = chat.add_message(self.user, strip_tags(message_body))
        message_obj = prepare_for_emit(serializers.MessageSerializer(message).data)
        user_chat_statuses = chat.user_chat_statuses
        user_chat_statuses_obj = prepare_for_emit(
            [serializers.UserChatStatusSerializer(ucs).data for ucs in user_chat_statuses.all()])

        for user in chat.users.all():
            for connection in self.connections.get(user, []):
                connection.emit('ev_message_sent', message_obj, user_chat_statuses_obj)

        # Activate any archived user_chat_statusses
        for user_chat_status in chat.user_chat_statuses.all().filter(status=UserChatStatus.ARCHIVED):
            user_chat_status.activate()
            chat_obj = prepare_for_emit(serializers.ChatSerializer(chat).data)
            for connection in self.connections.get(user_chat_status.user, []):
                connection.emit('ev_chat_created', chat_obj)

    @event('req_chat_activate')
    def chat_activate(self, chat_uuid):
        """
        Change the UI state to visible.
        """
        chat = Chat.objects.get(uuid=chat_uuid)
        if self.user in chat.users.all():
            user_chat_status = chat.user_chat_statuses.get(user=self.user)
            if user_chat_status.is_inactive:
                user_chat_status.activate()
                self.emit('ev_chat_activated', chat.uuid.hex)

    @event('req_chat_deactivate')
    def chat_deactivate(self, chat_uuid):
        """
        Change the UI state to invisible.
        """
        chat = Chat.objects.get(uuid=chat_uuid)
        if self.user in chat.users.all():
            user_chat_status = chat.user_chat_statuses.get(user=self.user)
            if user_chat_status.is_active:
                user_chat_status.deactivate()
                self.emit('ev_chat_deactivated', chat.uuid.hex)

    @event('req_chat_archive')
    def chat_archive(self, chat_uuid):
        """
        Archive the chat.
        """
        chat = Chat.objects.get(uuid=chat_uuid)
        if self.user in chat.users.all():
            user_chat_status = chat.user_chat_statuses.get(user=self.user)
            if not user_chat_status.is_archived:
                user_chat_status.archive()
                self.emit('ev_chat_archived', chat.uuid.hex)

    def on_disconnect(self):
        pass

    def on_close(self):
        pass


# Create chat router
ChatRouter = TornadioRouter(ChatConnection, user_settings={'websocket_check': True}, namespace='chat/socket.io')

# Create application
application = web.Application(
    ChatRouter.apply_routes([]),
    socket_io_port=8001,
)

if __name__ == "__main__":
    # import logging
    # logging.getLogger().setLevel(logging.DEBUG)

    SocketServer(application)
