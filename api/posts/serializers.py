from rest_framework import serializers
from .models import Post, PostComment, PostReaction, Hashtag
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    tagged_users = serializers.SlugRelatedField(
        many=True, slug_field="username", queryset=User.objects.all(), required=False
    )
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=150), required=False, write_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "image",
            "video",
            "created_at",
            "updated_at",
            "tagged_users",
            "hashtags",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        tagged_users = validated_data.pop("tagged_users", [])
        hashtag_data = validated_data.pop("hashtags", [])

        post = Post.objects.create(**validated_data)
        # post.hashtags.set(hashtag_data)

        hashtags_to_add = []

        if tagged_users:
            # print(f"Tagged users: {tagged_users}")
            post.tagged_users.set(tagged_users)

        if hashtag_data:
            print("Processing hashtags...")

            for tag in hashtag_data:
                cleaned_tag = tag.strip("#")
                hashtag, created = Hashtag.objects.get_or_create(tag=cleaned_tag)
                hashtag.usage += 1
                hashtag.save()
                hashtags_to_add.append(hashtag)

        print(hashtags_to_add)
        post.hashtags.add(*hashtags_to_add)

        return post

    def validate(self, data):
        if not (data.get("content") or data.get("image") or data.get("video")):
            raise serializers.ValidationError(
                "At least one of content, image, or video must be provided."
            )
        return data


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = PostComment
        fields = ["id", "post", "user", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "post", "created", "updated_at"]

    def validate(self, data):
        comment = data.get("comment")
        if not comment or len(comment.strip()) == 0:
            raise serializers.ValidationError("Comment cannot be empty.")
        if len(comment) > 500:
            raise serializers.ValidationError(
                "Comment is too long, max 500 characters."
            )
        return data


class PostReactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = PostReaction
        fields = ["id", "post", "user", "reaction_type", "created_at"]
        read_only_fields = ["id", "created_at"]


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["id", "tag", "usage"]
        read_only_fields = ["id", "usage"]
