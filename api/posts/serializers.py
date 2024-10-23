from rest_framework import serializers
from .models import Post, PostComment, PostReaction, Hashtag
from django.contrib.auth import get_user_model
import re

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
        content = validated_data.get("content", "")

        hashtag_pattern = r"#(\w+)"
        hashtags = re.findall(hashtag_pattern, content)

        tagged_user_pattern = r"@(\w+)"
        tagged_usernames = re.findall(tagged_user_pattern, content) 

        post = Post.objects.create(**validated_data)
        # post.hashtags.set(hashtag_data)

        

        if tagged_usernames:
            tagged_users = User.objects.filter(username__in=tagged_usernames)
            # print(f"Tagged users: {tagged_users}")
            post.tagged_users.set(tagged_users)

        if hashtags:
            #print("Processing hashtags...")
            hashtags_to_add = []
            for tag in hashtags:
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
        read_only_fields = ["id", "created_at", "user","post"]


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["id", "tag", "usage"]
        read_only_fields = ["id", "usage"]
