#from django.db import models
#from django.contrib.auth.models import User
#
#import choices
#
#
#class Conversation(models.Model):
#
#    def get_participants(self):
#        """
#        Return the users that have participated in this chat conversation.
#        """
#        return User.objects.filter(id__in=self.chat_lines.all().values('user'))
#
#
#class ChatUser(models.Model):
#    status = models.IntegerField(choices=choices.Status.all(), default=choices.Status.OFFLINE[0])
#    user = models.ForeignKey(User)
#
#    def get_online_contacts(self):
#        return ChatUser.objects.filter(status=choices.Status.ONLINE[0])
#
#    def get_offline_contacts(self):
#        return ChatUser.objects.filter(status=choices.Status.OFFLINE[0])
#
#    def __unicode__(self):
#        return unicode(self.user)
#
#
#class ChatLine(models.Model):
#    user = models.ForeignKey(ChatUser)
#    timestamp = models.DateTimeField(auto_now=True)
#    text = models.TextField()
#    conversation = models.ForeignKey(Conversation, related_name='chat_lines')
#
