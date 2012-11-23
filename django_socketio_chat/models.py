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

    def add_message(self, user, message):
        message = Message(chat=self, user=user, message=message)
        message.save()

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
    user = models.ForeignKey(User, related_name='messages')
    message = models.TextField()

    def __unicode__(self):
        return "{user} says \"{message}\" ({timestamp})".format(user=self.user, message=self.message, timestamp=self.timestamp)
