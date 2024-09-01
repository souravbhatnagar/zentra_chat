from django.db import models
from django.contrib.auth.models import User


class InterestMessage(models.Model):
    """
    Model representing an interest message sent from one user to another.

    Attributes:
    -----------
    sender : ForeignKey
        A reference to the User who sent the interest message. When the sender user is deleted,
        all related interest messages are also deleted.

    receiver : ForeignKey
        A reference to the User who received the interest message. When the receiver user is deleted,
        all related interest messages are also deleted.

    status : CharField
        The status of the interest message, indicating whether it is pending, accepted, or rejected.
        The maximum length of this field is 20 characters.
    """

    sender = models.ForeignKey(
        User, related_name="sent_interests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_interests", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
    )

    def __str__(self):
        """
        Returns a string representation of the InterestMessage instance.

        This string will include the sender's username and the status of the message.
        """
        return f"Interest from {self.sender.username} to {self.receiver.username} ({self.status})"


class Chat(models.Model):
    """
    Model representing a chat between two users.

    Attributes:
    -----------
    user1 : ForeignKey
        A reference to the first User in the chat. When this user is deleted, all related chats
        involving this user as 'user1' are also deleted.

    user2 : ForeignKey
        A reference to the second User in the chat. When this user is deleted, all related chats
        involving this user as 'user2' are also deleted.

    messages : TextField
        A field containing the chat messages exchanged between the two users, stored as text.
    """

    user1 = models.ForeignKey(
        User, related_name="chats_as_user1", on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User, related_name="chats_as_user2", on_delete=models.CASCADE
    )
    messages = models.TextField()

    def __str__(self):
        """
        Returns a string representation of the Chat instance.

        This string will include the usernames of the two users involved in the chat.
        """
        return f"Chat between {self.user1.username} and {self.user2.username}"
