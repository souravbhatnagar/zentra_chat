from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login
from .models import InterestMessage, Chat, User
from .serializers import InterestMessageSerializer, ChatSerializer, UserSerializer


class RegisterView(APIView):
    """
    View for user registration.

    Allows for the creation of new user accounts.
    Expects username, email, and password in the request data.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST requests for user registration.

        - Checks if the username already exists.
        - Creates a new user if the username does not exist.
        - Serializes and returns the created user data.

        Args:
            request: The HTTP request object containing user data.

        Returns:
            Response: The HTTP response with user data or error message.
        """
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.save()

        # Serialize the registered user
        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    View for user login.

    Authenticates users and provides login functionality.
    Expects username and password in the request data.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST requests for user login.

        - Authenticates the user with the provided username and password.
        - Logs in the user and returns the user data if successful.
        - Returns an error message if authentication fails.

        Args:
            request: The HTTP request object containing user credentials.

        Returns:
            Response: The HTTP response with user data or error message.
        """
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            # Serialize the logged-in user
            serializer = UserSerializer(user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )


class SendInterestView(APIView):
    """
    View for sending interest messages between users.

    Allows authenticated users to send an interest message to another user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        """
        Handle POST requests for sending an interest message.

        - Checks if an interest message already exists between the sender and receiver.
        - Creates a new interest message with a "pending" status if no existing message is found.
        - Serializes and returns the created interest message.

        Args:
            request: The HTTP request object containing user ID for the receiver.
            user_id: The ID of the user to whom the interest message is being sent.

        Returns:
            Response: The HTTP response with interest message data or error message.
        """
        sender = request.user
        receiver = User.objects.get(id=user_id)

        if InterestMessage.objects.filter(sender=sender, receiver=receiver).exists():
            return Response(
                {"error": "Interest already sent."}, status=status.HTTP_400_BAD_REQUEST
            )

        interest = InterestMessage.objects.create(
            sender=sender, receiver=receiver, status="pending"
        )

        # Serialize the created interest message
        serializer = InterestMessageSerializer(interest)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptInterestView(APIView):
    """
    View for accepting interest messages.

    Allows authenticated users to accept interest messages from other users.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        """
        Handle POST requests for accepting an interest message.

        - Retrieves the interest message with the given ID.
        - Checks if the status is "pending".
        - Updates the status to "accepted" and creates a chat between the users.
        - Serializes and returns the updated interest message.

        Args:
            request: The HTTP request object containing the message ID.
            message_id: The ID of the interest message to be accepted.

        Returns:
            Response: The HTTP response with updated interest message data or error message.
        """
        interest = InterestMessage.objects.get(id=message_id, receiver=request.user)
        if interest.status != "pending":
            return Response(
                {"error": "Interest is not pending."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interest.status = "accepted"
        interest.save()

        # Serialize the updated interest message
        serializer = InterestMessageSerializer(interest)

        # Create a chat if interest is accepted
        Chat.objects.create(user1=interest.sender, user2=interest.receiver)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RejectInterestView(APIView):
    """
    View for rejecting interest messages.

    Allows authenticated users to reject interest messages from other users.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        """
        Handle POST requests for rejecting an interest message.

        - Retrieves the interest message with the given ID.
        - Checks if the status is "pending".
        - Updates the status to "rejected".
        - Serializes and returns the updated interest message.

        Args:
            request: The HTTP request object containing the message ID.
            message_id: The ID of the interest message to be rejected.

        Returns:
            Response: The HTTP response with updated interest message data or error message.
        """
        interest = InterestMessage.objects.get(id=message_id, receiver=request.user)
        if interest.status != "pending":
            return Response(
                {"error": "Interest is not pending."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interest.status = "rejected"
        interest.save()

        # Serialize the updated interest message
        serializer = InterestMessageSerializer(interest)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatView(APIView):
    """
    View for accessing and managing chats.

    Allows authenticated users to view their chats and send new messages.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to retrieve all chats involving the authenticated user.

        - Filters chats where the user is either user1 or user2.
        - Serializes and returns the chat data.

        Args:
            request: The HTTP request object.

        Returns:
            Response: The HTTP response with chat data.
        """
        chats = Chat.objects.filter(user1=request.user) | Chat.objects.filter(
            user2=request.user
        )
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Handle POST requests to create or update a chat with a new message.

        - Retrieves or creates a chat between the authenticated user and another user.
        - Creates a new message and associates it with the chat.
        - Returns a success message.

        Args:
            request: The HTTP request object containing the user ID and message.

        Returns:
            Response: The HTTP response with a success message.
        """
        user1 = request.user
        user2_id = request.data.get("user2_id")
        message = request.data.get("message")

        user2 = User.objects.get(id=user2_id)

        # Find an existing chat or create a new one
        chat = Chat.objects.filter(user1=user1, user2=user2).first()
        if not chat:
            chat = Chat.objects.filter(user1=user2, user2=user1).first()

        if not chat:
            chat = Chat.objects.create(user1=user1, user2=user2)

        chat.objects.create(sender=user1, text=message)
        chat.save()

        return Response(
            {"message": "Message sent successfully."}, status=status.HTTP_200_OK
        )


class InterestMessageView(APIView):
    """
    View for retrieving interest messages.

    Allows authenticated users to view all interest messages where they are either the sender or receiver.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to retrieve all interest messages involving the authenticated user.

        - Filters interest messages where the user is either the sender or receiver.
        - Serializes and returns the interest message data.

        Args:
            request: The HTTP request object.

        Returns:
            Response: The HTTP response with interest message data.
        """
        # Fetch all interest messages where the user is either the sender or the receiver
        sent_interests = InterestMessage.objects.filter(sender=request.user)
        received_interests = InterestMessage.objects.filter(receiver=request.user)

        # Combine both querysets and serialize
        all_interests = sent_interests.union(received_interests)
        serializer = InterestMessageSerializer(all_interests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(ListAPIView):
    """
    View for listing users.

    Provides a list of all users except the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Retrieve the list of users excluding the authenticated user.

        Returns:
            QuerySet: The list of users excluding the authenticated user.
        """
        return User.objects.exclude(id=self.request.user.id)
