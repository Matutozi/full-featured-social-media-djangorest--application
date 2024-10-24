from rest_framework import serializers
from .models import User, ProfilePic, CoverPhoto, Follow
from drf_spectacular.utils import extend_schema_field


class FollowViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserSerializers(serializers.ModelSerializer):
    # followers = FollowViewSerializer(many=True, read_only=True, source="following")
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "role",
            "bio",
            "contact_info",
            "social_links",
            "followers",
            "following",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "password": {"write_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)  # to hash the passwoord

        instance.save()
        return instance

    def get_followers(self, obj):
        """Return a list of followers' usernames."""
        followers = Follow.objects.filter(follower=obj)
        print(followers)
        for follow in followers:
            print(follow)
            return follow.followed.username
        print("I am here")
        # return [follow.follower.username for follow in followers]

    def get_following(self, obj):
        """Return a list of users following usernames"""
        followers = Follow.objects.filter(follower=obj)
        print(followers)
        # print(f"print: {followers}")
        for follow in followers:
            print(follow)
            return follow.follower.username
        print("I am here")


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop("password", None)
        return representation


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "bio",
            "email",
            "contact_info",
            "social_links",
            "is_active",
        ]


class ProfilePicsSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = ProfilePic
        fields = ["id", "username", "image", "created_at", "updated_at"]
        extra_kwargs = {"user": {"read_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user

        profilepics = super().create(validated_data)
        return profilepics

    @extend_schema_field(str)
    def get_username(self, obj):
        return obj.user.username


class CoverPhotosSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = CoverPhoto
        fields = ["id", "username", "image", "created_at", "updated_at"]
        extra_kwargs = {"user": {"read_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user

        coverphoto = CoverPhoto(**validated_data)
        coverphoto.save()

        return coverphoto

    @extend_schema_field(str)
    def get_username(self, obj):
        return obj.user.username


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("follower", "followed", "created_at")


class BanUnbanSerializer(serializers.ModelField):
    class Meta:
        model = User
        fields = ["ban"]

    def update(self, instance, validated_data):
        instance.ban = validated_data.get("ban", instance.ban)
        instance.save()
        return instance
