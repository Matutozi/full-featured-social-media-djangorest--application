from .models import Message, Group, GroupMessage
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.serializers import UserSerializers
from django.db import models
from django.shortcuts import get_object_or_404

User = get_user_model()


class MessageSerializers(serializers.ModelSerializer):
    """Serializer to create a new message"""

    class Meta:
        model = Message
        fields = ["text", "attachment", "sender", "receiver", "id", "timestamp"]
        read_only_fields = ["sender"]

    def create(self, validated_data):
        validated_data["sender"] = self.context["request"].user
        return Message.objects.create(**validated_data)


class MessageListSerializer(serializers.ModelSerializer):
    """Serializer to list message details between users"""

    sender = UserSerializers()
    receiver = UserSerializers()

    class Meta:
        model = Message
        fields = ["sender", "receiver", "text", "attachment", "id", "timestamp"]
        ordering = ["-timestamp"]


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer to list conversation as between two users"""

    user = UserSerializers
    last_message = serializers.SerializerMethodField()

    class Meta:
        fields = ["user", "last_message"]

    def get_last_message(self, instance):
        """
        Get the latest message between the current user and another user (the receiver).
        """
        request_user = self.context["request"].user
        other_user = instance

        message = (
            (
                Message.objects.filter(
                    models.Q(sender=request_user, receiver=other_user)
                    | models.Q(sender=other_user, receiver=request_user)
                )
            )
            .order_by("-timestamp")
            .first()
        )

        if message:
            return MessageSerializers(instance=message).data
        else:
            return None


class ConversationDetailSerializers(serializers.ModelSerializer):
    """Serializer to display full conversation history between two users"""

    user = UserSerializers
    messages = serializers.SerializerMethodField()

    class Meta:
        fields = ["user", "messages"]

    def get_messages(self, instance):
        """
        Get the all messages between the current user and another user (the receiver).
        """
        request_user = self.context["request"].user
        other_user = instance

        messsages = Message.objects.filter(
            models.Q(sender=request_user, receiver=other_user)
            | models.Q(sender=other_user, receiver=request_user)
        ).order_by("_timestamp")

        return MessageSerializers(messsages, many=True).data


class GroupSerializers(serializers.ModelSerializer):
    """Serializer that creates a new group"""

    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Group
        fields = ["id", "group_name", "members", "created_at"]

    def create(self, validated_data):
        members_data = validated_data.pop("members", [])
        group = Group.objects.create(**validated_data)
        group.members.set(members_data)
        return group

    def update(self, instance, validated_data):
        instance.group_name = validated_data.get("group_name", instance.group_name)
        members_data = validated_data.pop("members", None)
        if members_data:
            instance.members.set(members_data)
        instance.save()
        return instance


class GroupMessageSerializer(serializers.ModelSerializer):
    """Serializet that"""

    sender = UserSerializers(read_only=True)

    class Meta:
        model = GroupMessage
        fields = ["id", "group", "sender", "text", "attachment", "timestamp"]

    def create(self, validated_data):
        request = self.context.get("request")
        if not request.user.is_authenticated:
            raise serializers.ValidationError("User must be logged in to send message")

        sender = request.user

        validated_data.pop("sender", None)
        group_id = validated_data.get("group")
        if not group_id:
            raise serializers.ValidationError("Group must be specified")

        group_instance = get_object_or_404(Group, id=group_id)
        validated_data.pop("sender", None)
        validated_data.pop("group", None)

        return GroupMessage.objects.create(sender=sender, **validated_data)
