from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Post, PostComment, PostReaction, Hashtag
from .serializers import (
    PostSerializer,
    PostCommentSerializer,
    PostReactionSerializer,
    HashtagSerializer,
)
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework import filters
from users.serializers import UserSerializers
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

User = get_user_model()


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Post created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Failed to create post",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PostListView(generics.ListAPIView):
    """Endpoint to retrieve all posts, or filter by username."""

    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def get_queryset(self):
        username = self.request.query_params.get("username", None)
        if username:
            return Post.objects.filter(user__username=username)
        return Post.objects.all()


class PostView(APIView):
    """
    Retrieve, update, or delete a post.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def get_object(self, post_id):
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id, format=None):
        """Retrieve a post"""
        post = self.get_object(post_id)
        serializer = self.serializer_class(post)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Post successfully retrieved",
            "data": serializer.data,
        }
        return Response(response_data)

    def patch(self, request, post_id, format=None):
        """Update a post"""
        post = self.get_object(post_id)

        if post.user != request.user:
            return Response(
                {
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "You do not have permission to update this post",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "Post updated successfully",
                "data": serializer.data,
            }
            return Response(response_data)

        response_data = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Failed to update post",
            "data": serializer.errors,
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, format=None):
        """Delete a post"""
        post = self.get_object(post_id)

        if post.user != request.user:
            return Response(
                {
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "You do not have permission to delete this post",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        post.delete()
        return Response(
            {
                "status_code": status.HTTP_204_NO_CONTENT,
                "message": "Post deleted successfully.",
                "data": {},
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class PostCommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostCommentSerializer
    lookup_field = "post_id"

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        if not Post.objects.filter(id=post_id).exists():
            raise NotFound("Post not found.")
        return PostComment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs["post_id"]
        serializer.save(post_id=post_id, user=self.request.user)


class PostReactionCreateView(generics.CreateAPIView):
    """View that adds a reaction to a post"""

    serializer_class = PostReactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        if not Post.objects.filter(id=post_id).exists():
            raise NotFound("Post not found.")
        user = self.request.user
        reaction_type = self.kwargs["reaction_type"]

        existing_reaction = PostReaction.objects.filter(
            post_id=post_id, user=user
        ).first()
        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
        else:
            serializer.save(post_id=post_id, user=user, reaction_type=reaction_type)


class SearchView(generics.ListAPIView):
    """View that searches for post, user, hashtags"""

    filter_backends = [filters.SearchFilter]
    search_field = ["content", "user__username", "hashtags__tag"]

    def get_queryset(self):
        query_type = self.request.GET.get("type")

        if query_type == "user":
            return User.objects.all()

        elif query_type == "hashtag":
            return Hashtag.objects.all()
        return Post.objects.all()

    def get_serializer_class(self):
        query_type = self.request.GET.get("type")

        if query_type == "user":
            return UserSerializers

        elif query_type == "hashtag":
            return HashtagSerializer

        return PostSerializer


class TrendingHashtagsView(generics.ListAPIView):
    """
    Returns the top 10 trending hashtags.
    """

    queryset = Hashtag.objects.order_by("-usage")[:10]
    serializer_class = HashtagSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SuggestedUsersView(generics.ListAPIView):
    """
    Suggest users to follow based on mutual connections or similar interests.
    """

    serializer_class = UserSerializers

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.exclude(id__in=current_user.followers.all())[:10]
