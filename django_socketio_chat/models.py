from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

from uuidfield import UUIDField


class ChatSession(models.Model):
    """
    Model for storing session state (signed_in/ signed_off/ invisible)
    """
    SIGNED_OFF = 0
    SIGNED_IN = 1
    INVISBLE = 2

    SESSION_STATUS_CHOICES = (
        (SIGNED_OFF, 'Signed off'),
        (SIGNED_IN, 'Signed in'),
        (INVISBLE, 'Invisible')
    )

    user = models.ForeignKey(User, related_name='chat_session')
    status = models.IntegerField(choices=SESSION_STATUS_CHOICES, default=SIGNED_OFF)

    # TODO extract into separate function that can be easily overridden

    @property
    def users_that_see_me(self):
        return User.objects.exclude(pk=self.user.pk).filter(chat_session__status=SIGNED_IN)

    @property
    def users_that_i_see(self):
        return User.objects.exclude(pk=self.user.pk).filter(chat_session__status=self.SIGNED_IN)

    @property
    def chats(self):
        return [ ucs.chat for ucs in UserChatStatus.objects.filter(user=self.user).exclude(status=UserChatStatus.ARCHIVED)]

    def sign_in(self):
        self.status = self.SIGNED_IN
        self.save()

    @property
    def is_signed_in(self):
        return self.status == self.SIGNED_IN

    def sign_off(self):
        self.status = self.SIGNED_OFF
        self.save()

    @property
    def is_signed_off(self):
        return self.status == self.SIGNED_OFF

    def go_invisible(self):
        self.status = self.INVISBLE
        self.save()

    @property
    def is_invisible(self):
        return self.status == self.INVISBLE


class Chat(models.Model):
    uuid = UUIDField(auto=True)
    started = models.DateTimeField('started', editable=False, auto_now_add=True)
    users = models.ManyToManyField(User, related_name='chats', through='UserChatStatus')

    def __unicode__(self):
        users_str = ', '.join([user.username for user in self.users.all()])
        message_count = len(self.messages.all())
        return "{users} - {message_count} messages (started {started})".format(users=users_str,
                                                                               message_count=message_count,
                                                                               started=self.started)

    @classmethod
    def start(cls, chat_user, users):
        chat_users = [chat_user,] + users
        chat = cls()
        chat.save()
        chat.add_users(chat_users)
        return chat

    def add_users(self, users):
        for user in users:
            user_chat_status = UserChatStatus(user=user, chat=self)
            user_chat_status.save()

    def add_message(self, user_from, message):
        message = Message(chat=self, user_from=user_from, message_body=message)
        message.save()
        return message


    def leave(self, user):
        user_chat_status = self.user_chat_statuses.get(user=user)
        user_chat_status.left = datetime.now()
        user_chat_status.status = UserChatStatus.INACTIVE
        user_chat_status.save()


class UserChatStatus(models.Model):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    CHAT_STATUS_CHOICES = (
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
    )

    user = models.ForeignKey(User, related_name='user_chat_statuses')
    chat = models.ForeignKey(Chat, related_name='user_chat_statuses')
    status = models.CharField(max_length=8, choices=CHAT_STATUS_CHOICES, default=ACTIVE)
    joined = models.DateTimeField('joined_timestamp', editable=False, auto_now_add=True)
    left = models.DateTimeField('left_timestamp', editable=False, blank=True, null=True)
    unseen_message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = (('user', 'chat'),)
        verbose_name_plural = 'user chat statuses'

    def __unicode__(self):
        return "{user} in chat \"{chat}\" ({status})".format(user=self.user, chat=self.chat, status=self.status)

    @property
    def is_active(self):
        return self.status == self.ACTIVE

    @property
    def is_inactive(self):
        return self.status == self.INACTIVE

    @property
    def is_archived(self):
        return self.status == self.ARCHIVED

    def activate(self):
        self.status = self.ACTIVE
        self.save()

    def deactivate(self):
        self.status = self.INACTIVE
        self.save()

    def archive(self):
        self.status = self.ARCHIVED
        self.save()


class Message(models.Model):
    uuid = UUIDField(auto=True)
    timestamp = models.DateTimeField('timestamp', editable=False, auto_now_add=True)
    chat = models.ForeignKey(Chat, related_name='messages')
    user_from = models.ForeignKey(User, related_name='messages')
    message_body = models.TextField()

    def __unicode__(self):
        return "{user} says \"{message}\" ({timestamp})".format(user=self.user_from, message=self.message_body, timestamp=self.timestamp)

    def save(self):
        super(Message, self).save() # First save this model, so that we have an id
        for user in self.chat.users.all().exclude(id=self.user_from.id):
            if self.chat.user_chat_statuses.get(user=user).status == UserChatStatus.ACTIVE:
                 UserMessageStatus.objects.create(user=user, message=self, is_read=True)
            else:
                 UserMessageStatus.objects.create(user=user, message=self)


class UserMessageStatus(models.Model):
    """
    Through-table that keeps track of the read-status of messages.
    Upon every message being created, a record of this table must be created
    for every user that is listening in on the chat, excluding the user that
    sent the message.

    OnReceive: if chat is active: setMessageRead(message, user)
    OnChatActivate: setAllMessagesRead(chat.messages, user)
    """
    user = models.ForeignKey(User, related_name='user_message_statuses')
    message = models.ForeignKey(Message, related_name='user_message_statuses')
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('message', 'user')

