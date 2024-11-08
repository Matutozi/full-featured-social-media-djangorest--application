import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Post, PostComment, PostReaction, Hashtag
from django.contrib.auth import get_user_model

User = get_user_model()


class PostTests(TestCase):
    def setUp(self):
        """
        Set up any necessary data for the tests
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@gmail.com", username="test", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)


        self.post = Post.objects.create(user=self.user, content="Sample content")
        self.post_id = self.post.id
        
        self.create_url = reverse("create-post")
        self.list_url = reverse("list-posts")
        self.post_url = reverse("post-detail", kwargs={"post_id": self.post_id})
        self.comment_url = reverse("post-comment", kwargs={"post_id": self.post_id})
        self.reaction_url = reverse(
            "post_reaction", kwargs={"post_id": self.post_id, "reaction_type": "like"}
        )
        self.search_url = reverse("search")
        self.trending_url = reverse("trending_hashtags")
        self.suggested_users_url = reverse("suggested_users")

        self.valid_post_data = {"content": "This is a test post content."}

    def test_create_post(self):
        """
        Test that we can create a post
        """
        response = self.client.post(
            self.create_url, self.valid_post_data, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )  # 201 means the post was created

    def test_list_posts(self):
        """
        Test that we can list all posts
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_detail(self):
        """
        Test that we can get details of a specific post by post_id
        """
        # First, we need to create a post with the post_id
        # Create a new post using the valid data
        self.client.post(self.create_url, self.valid_post_data, format="json")

        # Now, retrieve that specific post using the UUID
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment(self):
        """
        Test that we can create a comment on a specific post
        """
        # Create a post first
        self.client.post(self.create_url, self.valid_post_data, format="json")

        # Create comment data (assuming the API requires this format)
        comment_data = {"comment": "This is a test comment"}
        response = self.client.post(self.comment_url, comment_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_reaction(self):
        """
        Test that we can add a reaction to a post
        """
        # Create a post first
        self.client.post(self.create_url, self.valid_post_data, format="json")

        # Reaction data (assuming the API allows "like" reactions)
        reaction_data = {"reaction_type": "like"}
        response = self.client.post(self.reaction_url, reaction_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_search(self):
        """
        Test the search functionality
        """
        response = self.client.get(self.search_url, {"q": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trending_hashtags(self):
        """
        Test that we can get the trending hashtags
        """
        response = self.client.get(self.trending_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suggested_users(self):
        """
        Test that we can get the suggested users
        """
        response = self.client.get(self.suggested_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_not_allowed_for_create_post_on_get(self):
        """
        Test that a GET request to create a post endpoint returns a 405 Method Not Allowed
        """
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_not_allowed_for_post_reaction_on_get(self):
        """
        Test that a GET request to post reaction endpoint returns a 405 Method Not Allowed
        """
        response = self.client.get(self.reaction_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_not_allowed_for_post_comment_on_get(self):
        """
        Test that a GET request to post comment endpoint returns a 405 Method Not Allowed
        """
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
