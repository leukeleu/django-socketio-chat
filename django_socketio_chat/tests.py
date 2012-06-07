from django.utils import unittest

import models


class ConversationTestCase(unittest.TestCase):
    def setUp(self):
        user1 = models.User(username='testuser1')
        user1.save()
        self.chat_user1 = models.ChatUser(user=user1)
        self.chat_user1.save()
        user2 = models.User(username='testuser2')
        user2.save()
        self.chat_user2 = models.ChatUser(user=user2)
        self.chat_user2.save()
        self.conversation = models.Conversation()
        self.conversation.save()
        self.chat_line1 = models.ChatLine.objects.create(user=self.chat_user1, text='Test line 1.', conversation=self.conversation)
        self.chat_line2 = models.ChatLine.objects.create(user=self.chat_user2, text='Test line 2.', conversation=self.conversation)

    def test_get_participants(self):
        """
        Test Conversation.test_get_participants returns all chat participants in the conversation.
        """

        participants = self.conversation.get_participants()
        self.assertEqual(len(participants), 2)
        self.assertTrue(self.user1 in participants)
        self.assertTrue(self.user2 in participants)
