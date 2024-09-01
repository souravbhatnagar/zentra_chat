from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, InterestMessage

from channels.testing import ChannelsLiveServerTestCase
from channels.testing import WebsocketCommunicator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from backend.consumers import ChatConsumer


class UserTests(APITestCase):
    """
    Test cases for user-related functionalities, including user registration, login, and fetching user lists.
    """

    def setUp(self):
        """
        Set up test data for the user tests.

        Creates two test users with different usernames and passwords.
        """
        self.user = User.objects.create_user(
            username="testuser2", password="testpassword123"
        )
        self.user = User.objects.create_user(
            username="testuser3", password="testpassword123"
        )

    def test_register_user(self):
        """
        Test the user registration endpoint.

        This test verifies that a new user can be registered successfully and checks if the user count increases by one.
        """
        url = reverse("register")
        data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "testuser@example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_login_user(self):
        """
        Test the user login endpoint.

        This test verifies that a registered user can log in successfully and checks if the username is returned in the response.
        """
        url = reverse("login")
        data = {"username": "testuser2", "password": "testpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            "username" in response.data and response.data["username"] == "testuser2"
        )

    def test_user_list(self):
        """
        Test fetching the list of users.

        This test verifies that a logged-in user can fetch the list of other users.
        """
        self.client.login(username="testuser2", password="testpassword123")
        url = reverse("users")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class InterestTests(APITestCase):
    """
    Test cases for interest-related functionalities, including sending, accepting, and rejecting interests.
    """

    def setUp(self):
        """
        Set up test data for interest message tests.

        Creates two sender users, one receiver user, and an interest message with pending status.
        """
        self.sender = User.objects.create_user(
            username="sender", password="password123"
        )
        self.sender2 = User.objects.create_user(
            username="sender2", password="password123"
        )
        self.receiver = User.objects.create_user(
            username="receiver", password="password123"
        )
        self.interest = InterestMessage.objects.create(
            sender=self.sender, receiver=self.receiver, status="pending"
        )

    def test_send_interest(self):
        """
        Test sending an interest message.

        This test verifies that a logged-in user can send an interest message to another user and checks if the message is created with a pending status.
        """
        self.client.login(username="sender2", password="password123")
        url = reverse("send-interest", kwargs={"user_id": self.receiver.id})
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sender"], self.sender2.id)
        self.assertEqual(response.data["receiver"], self.receiver.id)
        self.assertEqual(response.data["status"], "pending")

    def test_accept_interest(self):
        """
        Test accepting an interest message.

        This test verifies that a receiver can accept an interest message and checks if the status is updated to accepted.
        """
        self.client.login(username="receiver", password="password123")
        url = reverse(
            "accept-interest",
            kwargs={"message_id": self.interest.id},
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, "accepted")

    def test_reject_interest(self):
        """
        Test rejecting an interest message.

        This test verifies that a receiver can reject an interest message and checks if the status is updated to rejected.
        """
        self.client.login(username="receiver", password="password123")
        url = reverse(
            "reject-interest",
            kwargs={"message_id": self.interest.id},
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, "rejected")


class ChatTests(APITestCase, ChannelsLiveServerTestCase):
    """
    Test cases for chat-related functionalities, including accessing chat and testing WebSocket communication.
    """

    def setUp(self):
        """
        Set up test data for chat tests.

        Creates two users and an accepted interest message between them.
        """
        self.sender = User.objects.create_user(
            username="sender", password="password123"
        )
        self.receiver = User.objects.create_user(
            username="receiver", password="password123"
        )
        self.interest = InterestMessage.objects.create(
            sender=self.sender, receiver=self.receiver, status="accepted"
        )

    def test_access_chat(self):
        """
        Test accessing the chat.

        This test verifies that a logged-in user with an accepted interest message can access the chat interface.
        """
        self.client.login(username="sender", password="password123")
        url = reverse("chat")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_chat_consumer(self):
        """
        Test WebSocket communication for a single user in the chat.

        This asynchronous test verifies that a user can connect to the WebSocket, send a message, and receive it back.
        """
        # Create a communicator for the consumer
        communicator = WebsocketCommunicator(
            application=ProtocolTypeRouter(
                {
                    "websocket": URLRouter(
                        [
                            path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
                        ]
                    )
                }
            ),
            path="/ws/chat/test-room/",
        )

        # Test connection
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Test sending a message through the WebSocket
        await communicator.send_json_to({"message": "Hello!"})

        # Test receiving the message
        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], "Hello!")

        # Test disconnecting
        await communicator.disconnect()

    async def test_multiple_users_in_chat(self):
        """
        Test WebSocket communication for multiple users in the same chat room.

        This asynchronous test verifies that multiple users can connect to the same chat room, send, and receive messages.
        """
        application = ProtocolTypeRouter(
            {
                "websocket": URLRouter(
                    [
                        path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
                    ]
                )
            }
        )
        communicator1 = WebsocketCommunicator(application, "/ws/chat/test-room/")
        communicator2 = WebsocketCommunicator(application, "/ws/chat/test-room/")

        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()

        self.assertTrue(connected1)
        self.assertTrue(connected2)

        await communicator1.send_json_to({"message": "Hello from user 1"})
        response2 = await communicator2.receive_json_from()

        self.assertEqual(response2["message"], "Hello from user 1")

        await communicator1.disconnect()
        await communicator2.disconnect()
