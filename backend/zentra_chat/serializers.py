from rest_framework import serializers
from .models import InterestMessage, Chat, User


class InterestMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the InterestMessage model.

    This serializer handles the conversion of InterestMessage instances to JSON format
    and vice versa. It includes all fields of the InterestMessage model.
    """

    class Meta:
        model = InterestMessage
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model.

    This serializer handles the conversion of Chat instances to JSON format and vice versa.
    It includes all fields of the Chat model.
    """

    class Meta:
        model = Chat
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer handles the conversion of User instances to JSON format and vice versa.
    It includes only the 'id', 'username', and 'email' fields of the User model.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email"]
