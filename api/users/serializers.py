from rest_framework import serializers
from .models import User, ProfilePic


class UserSerializers(serializers.ModelSerializer):
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


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


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
    class Meta:
        model = ProfilePic
        flelds = ["id", "user", "image", "created_at", "updated_at"]

        extra_kwargs = ["id", "created_at", "updated_at"]
