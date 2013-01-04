from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

from uuidfield import UUIDField


class Chat(models.Model):
    uuid = UUIDField(auto=True)
    started = models.DateTimeField('started', editable=False, auto_now_add=True)
    users = models.ManyToManyField(User, related_name='chats', through='UserChatStatus')

    def __unicode__(self):
        users_str = ', '.join([user.username for user in self.users.all()])
        message_count = len(self.messages.all())
        return "{users} - {message_count} messages (started {started})".format(users=users_str, message_count=message_count, started=self.started)

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

    def activate(self, user):
        user_chat_status = self.user_chat_statuses.get(user=user)
        user_chat_status.status = UserChatStatus.ACTIVE
        user_chat_status.save()

    def deactivate(self, user):
        user_chat_status = self.user_chat_statuses.get(user=user)
        user_chat_status.status = UserChatStatus.INACTIVE
        user_chat_status.save()

    def archive(self, user):
        user_chat_status = self.user_chat_statuses.get(user=user)
        user_chat_status.status = UserChatStatus.ARCHIVED
        user_chat_status.save()

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
    status = models.CharField(max_length=8, choices=CHAT_STATUS_CHOICES, default=INACTIVE)
    joined = models.DateTimeField('joined_timestamp', editable=False, auto_now_add=True)
    left = models.DateTimeField('left_timestamp', editable=False, blank=True, null=True)
    unseen_message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = (('user', 'chat'),)
        verbose_name_plural = 'user chat statuses'

    def __unicode__(self):
        return "{user} in chat \"{chat}\" ({status})".format(user=self.user, chat=self.chat, status=self.status)


class Message(models.Model):
    uuid = UUIDField(auto=True)
    timestamp = models.DateTimeField('timestamp', editable=False, auto_now_add=True)
    chat = models.ForeignKey(Chat, related_name='messages')
    user_from = models.ForeignKey(User, related_name='messages')
    message_body = models.TextField()

    def __unicode__(self):
        return "{user} says \"{message}\" ({timestamp})".format(user=self.user, message=self.message, timestamp=self.timestamp)

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

