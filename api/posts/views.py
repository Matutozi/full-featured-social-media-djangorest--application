from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Post
from .serializers import PostSerializer
from django.http import Http404


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"request": request})
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

    def get_object(self, post_id):
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id, format=None):
        """Retrieve a post"""
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
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

        serializer = PostSerializer(post, data=request.data, partial=True)
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