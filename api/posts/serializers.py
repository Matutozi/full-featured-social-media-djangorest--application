from rest_framework import serializers
from .models import Post, PostComment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "user", "content", "image", "video", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def validate(self, data):
        if not (data.get("content") or data.get("image") or data.get("video")):
            raise serializers.ValidationError(
                "At least one of content, image, or video must be provided."
            )
        return data


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ["id", "post", "user", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "post", "created", "updated_at"]
