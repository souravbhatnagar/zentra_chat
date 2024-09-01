"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from zentra_chat.views import (
    RegisterView,
    LoginView,
    InterestMessageView,
    ChatView,
    UserListView,
    SendInterestView,
    AcceptInterestView,
    RejectInterestView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="users"),
    path(
        "users/<int:user_id>/send-interest/",
        SendInterestView.as_view(),
        name="send-interest",
    ),
    path("interest-messages/", InterestMessageView.as_view(), name="interest-message"),
    path(
        "interest-messages/<int:message_id>/accept/",
        AcceptInterestView.as_view(),
        name="accept-interest",
    ),
    path(
        "interest-messages/<int:message_id>/reject/",
        RejectInterestView.as_view(),
        name="reject-interest",
    ),
    path("chat/", ChatView.as_view(), name="chat"),
]
