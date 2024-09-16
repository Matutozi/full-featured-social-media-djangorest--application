from rest_framework import serializers
from .models import User


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'role', 
            'bio', 'contact_info', 'social_links', 'followers', 
            'created_at', 'updated_at'
        ]

        extra_kwargs = {
            'password': {'write_only': True}, 
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password) #to hash the passwoord

        instance.save()
        return instance