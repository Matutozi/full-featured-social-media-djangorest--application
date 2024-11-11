from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .models import Message, Group, GroupMessage

User = get_user_model()


class MessagingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@email.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@email.com", password="password123"
        )
        self.group = Group.objects.create(group_name="Test Group")
        self.client.force_authenticate(user=self.user1)

    def test_create_message(self):
        """Test creating a message between two users"""
        url = reverse("create_message")
        data = {"receiver": self.user2.id, "text": "Hello, user2!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Message Sent", response.data["message"])

    def test_list_messages(self):
        """Test listing all messages between two users"""
        Message.objects.create(sender=self.user1, receiver=self.user2, text="Hello!")
        Message.objects.create(sender=self.user2, receiver=self.user1, text="Hi!")

        url = reverse("message_list", kwargs={"receiver_id": self.user2.id})
        response = self.client.get(url)
        """ print(response.data)
        print("I am here")
        print(response.json())"""

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)

    def test_delete_message(self):
        """Test deleting a message by the sender"""
        message = Message.objects.create(
            sender=self.user1, receiver=self.user2, text="Hello!"
        )
        url = reverse("message_delete", kwargs={"message_id": message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_update_message(self):
        """Test updating message content by sender"""
        message = Message.objects.create(
            sender=self.user1, receiver=self.user2, text="Hello!"
        )
        url = reverse("message_update", kwargs={"message_id": message.id})
        data = {"text": "Updated content"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message.refresh_from_db()
        self.assertEqual(message.text, "Updated content")

    def test_list_conversations(self):
        """Test listing conversations with users who have exchanged messages"""
        Message.objects.create(sender=self.user1, receiver=self.user2, text="Hello!")
        url = reverse("conversation_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user2.username, response.data["data"][0]["username"])

    def test_create_group(self):
        """Test creating a new group"""
        url = reverse("create_group")
        data = {"group_name": "New Group", "creator": self.user1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["group_name"], "New Group")

    def test_create_group_message(self):
        """Test creating a message within a group"""
        url = reverse("create_group_message", kwargs={"group_id": self.group.id})
        data = {"text": "Hello, group!"}
        response = self.client.post(url, data)
        """print("Response Data:", response.data)  # Print response content for debug
        print("Response Status Code:", response.status_code)"""
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_group_messages(self):
        """Test listing all messages within a group"""
        GroupMessage.objects.create(
            sender=self.user1, group=self.group, text="Hello, group!"
        )
        url = reverse("group_message_list", kwargs={"group_id": self.group.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_delete_group_message(self):
        """Test deleting a message from a group"""
        group_message = GroupMessage.objects.create(
            sender=self.user1, group=self.group, text="Hello, group!"
        )
        url = reverse("delete_group_message", kwargs={"pk": group_message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GroupMessage.objects.filter(id=group_message.id).exists())
