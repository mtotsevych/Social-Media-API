from django.urls import path

from user.views import (
    UserLoginView,
    UserCreateView,
    UserLogoutView,
    UserListView,
    UserYourProfileView,
    UserOtherProfileView,
    UserSubscribeView,
    UserUnsubscribeView,
    PostCreateView,
    PostListView,
)

app_name = "user"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path(
        "users/me/",
        UserYourProfileView.as_view(),
        name="user-me"
    ),
    path(
        "users/<int:pk>/",
        UserOtherProfileView.as_view(),
        name="user-other"
    ),
    path(
        "users/<int:pk>/subscribe/",
        UserSubscribeView.as_view(),
        name="user-subscribe"),
    path(
        "users/<int:pk>/unsubscribe/",
        UserUnsubscribeView.as_view(),
        name="user-unsubscribe"
    ),
    path(
        "posts/create/",
        PostCreateView.as_view(),
        name="post-create"
    ),
    path(
        "posts/",
        PostListView.as_view(),
        name="post-list"
    ),
]
