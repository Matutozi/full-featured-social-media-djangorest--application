from django.test import TestCase
from django.urls import reverse
from .models import User, Follow
from rest_framework.test import APIClient
import json


class UserTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="admin123"
        )
        self.client.force_authenticate(user=self.user)

    def test_register_user(self):
        """Test user registration view"""
        url = reverse("register")
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "username": "newuser",
            "first_name": "new",
            "last_name": "user",
        }
        response = self.client.post(url, data)

        # if response.status_code != 200:
        # print(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login_user(self):
        """Test user login view"""
        url = reverse("login")  # Adjust the view name as necessary
        data = {"email": "testuser@example.com", "password": "password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json().get("data", {}))

    def test_get_user_detail(self):
        """Test retrieving user details view"""
        url = reverse("user_profile", kwargs={"pk": self.user.pk})
        self.client.login(email="testuser@example.com", password="password123")
        response = self.client.get(url)
        # print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Message Sent")

    def test_update_user_profile(self):
        """Test updating user profile"""
        self.client.login(email="testuser@example.com", password="password123")
        url = reverse("user_profile", args=[self.user.pk])
        data = {
            "username": "updateduser",
            "email": "newemail@example.com",
            "bio": "new bio",
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_follow_user(self):
        """Test following another user"""
        other_user = User.objects.create_user(
            email="otheruser@example.com", username="otheruser", password="password123"
        )
        self.client.login(email="testuser@example.com", password="password123")
        url = reverse("follow", args=[other_user.pk])
        response = self.client.post(url)
        # print(response.json())
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Follow.objects.filter(follower=self.user, followed=other_user).exists()
        )

    def test_unfollow_user(self):
        """Test unfollowing a user"""
        other_user = User.objects.create_user(
            email="otheruser@example.com", username="otheruser", password="password123"
        )
        Follow.objects.create(follower=self.user, followed=other_user)
        self.client.login(email="testuser@example.com", password="password123")
        url = reverse("follow", args=[other_user.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Follow.objects.filter(follower=self.user, followed=other_user).exists()
        )

    def test_ban_user(self):
        """Test banning a user as an admin"""
        self.client.login(email="admin@example.com", password="admin123")

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("user-ban", args=[self.user.pk])
        response = self.client.patch(
            url, {"ban": True}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 202)
        self.user.refresh_from_db()
        self.assertTrue(self.user.ban)

    def test_unban_user(self):
        """Test unbanning a user as an admin"""
        self.user.ban = True
        self.user.save()
        self.client.login(email="admin@example.com", password="admin123")
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("user-unban", args=[self.user.pk])
        response = self.client.patch(
            url, {"ban": False}, content_type="application/json"
        )
        # print(response.json())
        self.assertEqual(response.status_code, 202)
        self.user.refresh_from_db()
        self.assertFalse(self.user.ban)
